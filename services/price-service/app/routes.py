import os
from flask import Blueprint, current_app, jsonify, request

api = Blueprint("api", __name__)


def _service():
    return current_app.config["PRICE_SERVICE"]


@api.get("/health")
def health():
    return jsonify(status="ok", service="price-service")


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
