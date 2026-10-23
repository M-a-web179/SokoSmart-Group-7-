"""Optional PostgreSQL persistence using the existing repository contract."""

from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from .models import PriceEntry


class PostgresPriceRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        return psycopg.connect(
            self.database_url, row_factory=dict_row, connect_timeout=5
        )

    def initialize(self) -> None:
        """Explicit development setup; never run schema changes on app startup."""
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.execute(schema)

    def all(self) -> list[PriceEntry]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM prices ORDER BY id").fetchall()
        return [PriceEntry(**row) for row in rows]

    def add(
        self, crop, market, price, unit="kg", currency="RWF", reported_on=""
    ) -> PriceEntry:
        with self._connect() as conn:
            row = conn.execute(
                """INSERT INTO prices (crop, market, price, unit, currency, reported_on)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
                (crop, market, price, unit, currency, reported_on),
            ).fetchone()
        return PriceEntry(**row)
