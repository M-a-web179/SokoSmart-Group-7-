from datetime import date
from typing import Dict, List, Optional

from .repository import PriceRepository


class PriceService:
    def __init__(self, repo: PriceRepository) -> None:
        self.repo = repo

    def list_prices(self, crop: Optional[str] = None, market: Optional[str] = None) -> List[dict]:
        entries = self.repo.all()
        if crop:
            entries = [e for e in entries if e.crop.lower() == crop.strip().lower()]
        if market:
            entries = [e for e in entries if e.market.lower() == market.strip().lower()]
        return [e.to_dict() for e in entries]

    def _latest_per_market(self, crop: str) -> Dict[str, object]:
        latest = {}
        for e in self.repo.all():
            if e.crop.lower() != crop.strip().lower():
                continue
            current = latest.get(e.market)
            if current is None or (e.reported_on, e.id) > (current.reported_on, current.id):
                latest[e.market] = e
        return latest

    def compare_markets(self, crop: str) -> dict:
        """Latest price of one crop in every market, cheapest first."""
        latest = self._latest_per_market(crop)
        if not latest:
            raise LookupError(f"No prices found for crop '{crop}'")
        rows = sorted(latest.values(), key=lambda e: e.price)
        return {
            "crop": rows[0].crop,
            "cheapest_market": rows[0].market,
            "markets": [
                {
                    "market": e.market,
                    "price": e.price,
                    "currency": e.currency,
                    "unit": e.unit,
                    "reported_on": e.reported_on,
                }
                for e in rows
            ],
        }

    def summary(self) -> List[dict]:
        """Average/min/max price per crop, based on the latest price in each market."""
        crops = sorted({e.crop for e in self.repo.all()})
        result = []
        for crop in crops:
            rows = list(self._latest_per_market(crop).values())
            prices = [e.price for e in rows]
            cheapest = min(rows, key=lambda e: e.price)
            priciest = max(rows, key=lambda e: e.price)
            result.append({
                "crop": crop,
                "average_price": round(sum(prices) / len(prices), 2),
                "min_price": cheapest.price,
                "max_price": priciest.price,
                "cheapest_market": cheapest.market,
                "most_expensive_market": priciest.market,
                "markets_reporting": len(rows),
                "currency": rows[0].currency,
                "unit": rows[0].unit,
            })
        return result

    def add_price(self, data: dict) -> dict:
        crop = str(data.get("crop", "")).strip().title()
        market = str(data.get("market", "")).strip().title()
        if not crop:
            raise ValueError("'crop' is required")
        if not market:
            raise ValueError("'market' is required")
        try:
            price = float(data.get("price"))
        except (TypeError, ValueError):
            raise ValueError("'price' must be a number")
        if price <= 0:
            raise ValueError("'price' must be greater than 0")
        entry = self.repo.add(
            crop,
            market,
            price,
            unit=str(data.get("unit", "kg")),
            currency=str(data.get("currency", "RWF")).upper(),
            reported_on=str(data.get("reported_on") or date.today().isoformat()),
        )
        return entry.to_dict()
