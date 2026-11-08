"""Interactive USSD simulator for local demos (no extra dependencies).

Run the app first (python run.py), then:

    python ussd_simulator.py

It behaves like a feature phone: you see a menu, type a number, and the
session ends when the service replies END. ``00`` goes back, ``0`` exits.
"""

import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"


def post_ussd(text: str) -> str:
    data = urllib.parse.urlencode({
        "sessionId": "SIM-001",
        "phoneNumber": "+250700000000",
        "serviceCode": "*384*23#",
        "text": text,
    }).encode()
    req = urllib.request.Request(f"{BASE_URL}/ussd", data=data)
    with urllib.request.urlopen(req, timeout=5) as res:
        return res.read().decode()


def main() -> None:
    text = ""
    print(f"SokoSmart USSD simulator ({BASE_URL}/ussd)")
    print("Dial *384*23# to start. Type 'quit' to leave the simulator.\n")
    while True:
        try:
            body = post_ussd(text)
        except (urllib.error.URLError, OSError) as err:
            print(f"Cannot reach the server: {err}")
            print("Start it with: python run.py")
            return
        print(body, "\n")
        if body.startswith("END"):
            print("--- session ended --- dial again to restart ---\n")
            text = ""
            continue
        choice = input("Your selection: ").strip()
        if choice.lower() in {"quit", "exit"}:
            return
        if choice == "00" and "*" in text:
            text = text.rsplit("*", 1)[0]
        elif choice == "00":
            text = ""
        else:
            text = f"{text}*{choice}" if text else choice


if __name__ == "__main__":
    main()
