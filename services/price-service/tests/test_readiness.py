import json
import logging
from pathlib import Path

from app import create_app
from app.db import check_database
from app.logging_config import JsonFormatter

ROOT = Path(__file__).resolve().parents[1]

SEED = str(ROOT / "data" / "seed_prices.json")


def make_client(**overrides):
    config = {"TESTING": True, "SEED_FILE": SEED, "DATABASE_URL": ""}
    config.update(overrides)
    return create_app(config).test_client()


# ---------------------------------------------------------------- /health


def test_health_is_ok_even_when_database_is_down():
    client = make_client(DATABASE_URL="postgresql://x", DB_CHECK=lambda url, timeout: False)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok", "service": "price-service"}


# ---------------------------------------------------------------- /ready


def test_ready_without_database_configured():
    res = make_client().get("/ready")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ready", "checks": {"database": "not_configured"}}


def test_ready_when_database_answers():
    seen = {}

    def fake_check(url, timeout):
        seen.update(url=url, timeout=timeout)
        return True

    client = make_client(DATABASE_URL="postgresql://u:p@db:5432/x", DB_CHECK=fake_check, DB_CONNECT_TIMEOUT=2)
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.get_json()["checks"]["database"] == "ok"
    assert seen == {"url": "postgresql://u:p@db:5432/x", "timeout": 2}


def test_ready_returns_503_when_database_is_down():
    client = make_client(DATABASE_URL="postgresql://u:secret@db:5432/x", DB_CHECK=lambda url, timeout: False)
    res = client.get("/ready")
    assert res.status_code == 503
    assert res.get_json() == {"status": "not_ready", "checks": {"database": "unreachable"}}
    assert b"secret" not in res.data


def test_real_check_returns_false_for_unreachable_database(caplog):
    # Port 1 on localhost refuses connections immediately
    url = "postgresql://user:topsecret@127.0.0.1:1/none"
    with caplog.at_level(logging.WARNING):
        assert check_database(url, timeout=1) is False
    assert "topsecret" not in caplog.text


# ---------------------------------------------------------------- config


def test_database_url_comes_from_environment(monkeypatch):
    import importlib

    import app.config as config_module

    monkeypatch.setenv("DATABASE_URL", "postgresql://from-env/db")
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "7")
    reloaded = importlib.reload(config_module)
    try:
        assert reloaded.Config.DATABASE_URL == "postgresql://from-env/db"
        assert reloaded.Config.DB_CONNECT_TIMEOUT == 7
    finally:
        monkeypatch.delenv("DATABASE_URL")
        monkeypatch.delenv("DB_CONNECT_TIMEOUT")
        importlib.reload(config_module)


# ---------------------------------------------------------------- logging


def test_formatter_writes_one_json_object_per_line():
    record = logging.makeLogRecord(
        {"name": "t", "levelname": "INFO", "levelno": logging.INFO, "msg": "hello", "path": "/ready", "status": 200}
    )
    line = JsonFormatter().format(record)
    assert "\n" not in line
    data = json.loads(line)
    assert data["message"] == "hello"
    assert data["level"] == "INFO"
    assert data["path"] == "/ready"
    assert data["status"] == 200
    assert "timestamp" in data


def test_each_request_is_logged_as_json(capsys):
    client = make_client()
    res = client.get("/health", headers={"X-Request-ID": "abc123"})
    assert res.headers["X-Request-ID"] == "abc123"

    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()]
    access = [entry for entry in lines if entry["logger"] == "price_service.access"]
    assert access, "expected an access log line"
    entry = access[-1]
    assert entry["method"] == "GET"
    assert entry["path"] == "/health"
    assert entry["status"] == 200
    assert entry["request_id"] == "abc123"
    assert isinstance(entry["duration_ms"], float)


def test_request_id_is_generated_when_missing():
    res = make_client().get("/health")
    assert len(res.headers["X-Request-ID"]) == 32
