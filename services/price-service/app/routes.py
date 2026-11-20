from flask import Blueprint, current_app, jsonify, request

api = Blueprint("api", __name__)


def _service():
    return current_app.config["PRICE_SERVICE"]


@api.get("/health")
def health():
    """Liveness: the process is up and answering. No dependencies checked."""
    return jsonify(status="ok", service="price-service")


@api.get("/ready")
def ready():
    """Readiness: can this instance serve real traffic right now?

    Checks the database when DATABASE_URL is set. 200 means ready,
    503 tells a load balancer or deploy script to hold traffic.
    """
    url = current_app.config.get("DATABASE_URL", "")
    if not url:
        database = "not_configured"
    elif current_app.config["DB_CHECK"](url, current_app.config.get("DB_CONNECT_TIMEOUT", 3)):
        database = "ok"
    else:
        database = "unreachable"

    is_ready = database != "unreachable"
    body = {"status": "ready" if is_ready else "not_ready", "checks": {"database": database}}
    return jsonify(body), 200 if is_ready else 503


@api.get("/api/prices")
def list_prices():
    prices = _service().list_prices(request.args.get("crop"), request.args.get("market"))
    return jsonify(count=len(prices), prices=prices)


@api.post("/api/prices")
def add_price():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Request body must be a JSON object"), 400
    try:
        entry = _service().add_price(payload)
    except ValueError as err:
        return jsonify(error=str(err)), 400
    return jsonify(entry), 201


@api.get("/api/prices/summary")
def summary():
    return jsonify(summary=_service().summary())


@api.get("/api/crops/<crop>/compare")
def compare(crop):
    try:
        return jsonify(_service().compare_markets(crop))
    except LookupError as err:
        return jsonify(error=str(err)), 404
