"""Offline regressions for connection settings and the real deployment health gates."""
from contextlib import contextmanager
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

from jinja2 import Environment, StrictUndefined
import yaml


ANSIBLE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inventory", ANSIBLE / "inventory_from_terraform.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def terraform_outputs():
    values = {
        "bastion_public_ip": "203.0.113.10",
        "app_private_ip": "10.20.10.10",
        "ssh_user": "ubuntu",
        "ecr_repository_url": "111122223333.dkr.ecr.eu-west-1.amazonaws.com/sokosmart-price",
        "db_secret_arn": "arn:aws:secretsmanager:eu-west-1:111122223333:secret:demo-database",
        "unexpected_sensitive_output": "must-stay-out-of-generated-files",
    }
    return {key: {"value": value} for key, value in values.items()}


class InventoryTests(unittest.TestCase):
    def test_reads_windows_and_unix_output_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "outputs.json"
            for encoding in ("utf-8", "utf-8-sig", "utf-16"):
                with self.subTest(encoding=encoding):
                    path.write_text(json.dumps(terraform_outputs()), encoding=encoding)
                    self.assertEqual(inventory.read_outputs(path), terraform_outputs())

    def test_outputs_select_registry_without_copying_sensitive_outputs(self):
        text, settings = inventory.deployment_files(terraform_outputs(), "/tmp/demo_key", "commit123")
        self.assertEqual(settings["app_image"],
                         "111122223333.dkr.ecr.eu-west-1.amazonaws.com/sokosmart-price:commit123")
        self.assertEqual(settings["aws_region"], "eu-west-1")
        self.assertIn("203.0.113.10", text)
        self.assertIn("10.20.10.10", text)
        self.assertIn("ProxyCommand", text)
        self.assertNotIn("must-stay-out-of-generated-files", text + json.dumps(settings))

    def test_rejects_shell_injection_and_cross_account_outputs(self):
        with self.assertRaises(ValueError):
            inventory.deployment_files(terraform_outputs(), "/tmp/key;echo unsafe", "commit123")
        with self.assertRaises(ValueError):
            inventory.deployment_files(terraform_outputs(), "/tmp/key", "tag;echo unsafe")
        outputs = terraform_outputs()
        outputs["db_secret_arn"]["value"] = outputs["db_secret_arn"]["value"].replace(
            "111122223333", "444455556666")
        with self.assertRaises(ValueError):
            inventory.deployment_files(outputs, "/tmp/key", "commit123")

    def test_cli_preserves_existing_settings_and_writes_private_files(self):
        with tempfile.TemporaryDirectory(prefix="sokosmart-test-") as directory:
            root = Path(directory)
            target = root / "ansible"
            target.mkdir()
            script = target / "inventory_from_terraform.py"
            shutil.copy2(ANSIBLE / script.name, script)
            local = target / "local.yml"
            local.write_text("keep_this: unchanged\n")
            key = root / "demo_key"
            key.write_text("fixture only, not an SSH private key\n")
            outputs = root / "outputs.json"
            outputs.write_text(json.dumps(terraform_outputs()), encoding="utf-8-sig")
            command = [sys.executable, str(script), "--key", str(key),
                       "--outputs", str(outputs), "--image-tag", "commit123"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            generated = target / "terraform.generated.yml"
            before = generated.read_text()
            for path in (generated, target / "inventory.ini"):
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(generated.read_text(), before)
            self.assertEqual(local.read_text(), "keep_this: unchanged\n")


@contextmanager
def readiness_server(database, status):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                body, response_status = {"status": "ok"}, 200
            else:
                body, response_status = {"checks": {"database": database}}, status
            encoded = json.dumps(body).encode()
            self.send_response(response_status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class ReadinessTests(unittest.TestCase):
    def test_compose_gate_rejects_missing_or_unreachable_database(self):
        template = Environment(undefined=StrictUndefined).from_string(
            (ANSIBLE / "roles/app/templates/docker-compose.yml.j2").read_text())
        for database, status, expected_success in (("ok", 200, True),
                                                    ("not_configured", 200, False),
                                                    ("unreachable", 503, False)):
            with self.subTest(database=database), readiness_server(database, status) as port:
                compose = yaml.safe_load(template.render(
                    app_image="demo:commit123", app_name="demo", app_bind_address="127.0.0.1",
                    app_port=port, app_container_port=port, app_dir="/tmp/demo",
                    app_readiness_path="/ready"))
                command = compose["services"]["app"]["healthcheck"]["test"]
                result = subprocess.run([sys.executable, *command[2:]], capture_output=True)
                self.assertEqual(result.returncode == 0, expected_success)

    def test_ansible_gates_reject_missing_or_unreachable_database(self):
        executable = Path(sys.executable).with_name("ansible-playbook")
        if not executable.exists():
            executable = shutil.which("ansible-playbook")
        self.assertTrue(executable, "Install Ansible before running deployment tests")
        for role, register in (("app", "app_readiness"), ("proxy", "proxy_readiness")):
            tasks = yaml.safe_load((ANSIBLE / f"roles/{role}/tasks/main.yml").read_text())
            gate = next(task for task in tasks if task.get("register") == register)
            for database, status, expected_success in (("ok", 200, True),
                                                        ("not_configured", 200, False),
                                                        ("unreachable", 503, False)):
                with self.subTest(role=role, database=database), readiness_server(database, status) as port:
                    task = copy.deepcopy(gate)
                    task["retries"], task["delay"] = 1, 0
                    # Only redirect the real gate to an isolated local HTTP fixture.
                    if role == "proxy":
                        task["ansible.builtin.uri"]["url"] = f"http://127.0.0.1:{port}/ready"
                    play = [{"name": "Check deployment readiness policy", "hosts": "all",
                             "gather_facts": False,
                             "vars": {"app_port": port, "app_readiness_path": "/ready",
                                      "ansible_python_interpreter": sys.executable},
                             "tasks": [task]}]
                    with tempfile.TemporaryDirectory(prefix="sokosmart-gate-") as directory:
                        path = Path(directory) / "gate.yml"
                        path.write_text(yaml.safe_dump(play))
                        result = subprocess.run(
                            [str(executable), "-i", "localhost,", "-c", "local", str(path)],
                            capture_output=True, text=True, timeout=45)
                        self.assertEqual(result.returncode == 0, expected_success,
                                         result.stdout[-3000:] + result.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()
