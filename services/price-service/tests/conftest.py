import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": "",
            "SEED_FILE": str(ROOT / "data" / "seed_prices.json"),
        }
    )
    return app.test_client()
