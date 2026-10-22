import json
from pathlib import Path
from typing import List

from .models import PriceEntry


class InMemoryPriceRepository:
    def __init__(self) -> None:
        self._entries: List[PriceEntry] = []
        self._next_id = 1

    def all(self) -> List[PriceEntry]:
        return list(self._entries)

    def add(self, crop, market, price, unit="kg", currency="RWF", reported_on="") -> PriceEntry:
        entry = PriceEntry(self._next_id, crop, market, price, unit, currency, reported_on)
        self._entries.append(entry)
        self._next_id += 1
        return entry

    def load_seed(self, path: str) -> None:
        file = Path(path)
        if not file.exists():
            return
        for row in json.loads(file.read_text(encoding="utf-8")):
            self.add(
                row["crop"],
                row["market"],
                row["price"],
                row.get("unit", "kg"),
                row.get("currency", "RWF"),
                row.get("reported_on", ""),
            )
