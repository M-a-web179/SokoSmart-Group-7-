from dataclasses import asdict, dataclass


@dataclass
class PriceEntry:
    id: int
    crop: str
    market: str
    price: float
    unit: str = "kg"
    currency: str = "RWF"
    reported_on: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
