import pytest
from app.repository import InMemoryPriceRepository
from app.services import PriceService


def make_service():
    return PriceService(InMemoryPriceRepository())


def test_summary_average_uses_latest_price_per_market():
    s = make_service()
    s.add_price({"crop": "Maize", "market": "A", "price": 100, "reported_on": "2026-10-01"})
    s.add_price({"crop": "Maize", "market": "A", "price": 200, "reported_on": "2026-10-10"})
    s.add_price({"crop": "Maize", "market": "B", "price": 400, "reported_on": "2026-10-05"})
    row = s.summary()[0]
    assert row["average_price"] == 300.0
    assert row["cheapest_market"] == "A"


def test_zero_price_rejected():
    with pytest.raises(ValueError):
        make_service().add_price({"crop": "Maize", "market": "A", "price": 0})
