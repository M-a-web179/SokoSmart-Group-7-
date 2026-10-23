"""Run only against a dedicated empty test database, never production data."""

import os

import pytest
from app import create_app


@pytest.fixture()
def database_url():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a dedicated PostgreSQL test database")
    import psycopg
    from app.postgres_repository import PostgresPriceRepository

    repo = PostgresPriceRepository(url)
    repo.initialize()
    with psycopg.connect(url) as conn:
        conn.execute("TRUNCATE prices RESTART IDENTITY")
    yield url
    with psycopg.connect(url) as conn:
        conn.execute("TRUNCATE prices RESTART IDENTITY")


def test_postgres_prices_survive_app_restart(database_url):
    config = {"TESTING": True, "DATABASE_URL": database_url}
    first = create_app(config).test_client()
    response = first.post(
        "/api/prices", json={"crop": "Maize", "market": "Huye", "price": 410}
    )
    assert response.status_code == 201
    second = create_app(config).test_client()
    rows = second.get("/api/prices?crop=maize&market=huye").get_json()
    assert rows["count"] == 1
    assert rows["prices"][0] == response.get_json()
    assert (
        second.get("/api/prices/summary").get_json()["summary"][0]["average_price"]
        == 410
    )
    assert (
        second.get("/api/crops/maize/compare").get_json()["cheapest_market"] == "Huye"
    )


def test_postgres_treats_sql_text_as_data(database_url):
    app = create_app({"TESTING": True, "DATABASE_URL": database_url})
    client = app.test_client()
    market = "Huye'); DROP TABLE prices; --"
    response = client.post(
        "/api/prices", json={"crop": "Beans", "market": market, "price": 900}
    )
    assert response.status_code == 201
    assert client.get("/api/prices").get_json()["count"] == 1
    assert client.get("/api/prices").get_json()["prices"][0]["market"] == market.title()


def test_init_db_is_explicit_and_repeatable(database_url):
    app = create_app({"TESTING": True, "DATABASE_URL": database_url})
    client = app.test_client()
    client.post("/api/prices", json={"crop": "Rice", "market": "Huye", "price": 1000})
    runner = app.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code == 0
    assert runner.invoke(args=["init-db"]).exit_code == 0
    assert client.get("/api/prices").get_json()["count"] == 1
