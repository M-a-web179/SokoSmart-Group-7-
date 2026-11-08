from flask import Blueprint, current_app, request

from .ussd import UssdMenuHandler

ussd = Blueprint("ussd", __name__)


def _handler() -> UssdMenuHandler:
    return UssdMenuHandler(current_app.config["PRICE_SERVICE"])


@ussd.post("/ussd")
def ussd_callback():
    """USSD gateway callback (Africa's Talking style).

    The gateway sends form fields ``sessionId``, ``phoneNumber``,
    ``serviceCode`` and ``text``; we reply with plain text starting
    with CON (continue) or END (terminate).
    """
    text = request.form.get("text") or (request.get_json(silent=True) or {}).get("text", "")
    current_app.logger.info(
        "USSD session=%s phone=%s text=%r",
        request.form.get("sessionId", "-"),
        request.form.get("phoneNumber", "-"),
        text,
    )
    return _handler().handle(text), 200, {"Content-Type": "text/plain; charset=utf-8"}


@ussd.get("/ussd")
def ussd_info():
    return (
        (
            "SokoSmart USSD endpoint.\n"
            "POST to /ussd with form field 'text' (menu inputs joined by '*').\n"
            "Try it interactively: python ussd_simulator.py\n"
        ),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )
