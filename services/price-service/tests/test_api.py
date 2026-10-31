def test_health(client):
    assert client.get("/health").get_json()["status"] == "ok"


def test_list_all_prices(client):
    data = client.get("/api/prices").get_json()
    assert data["count"] == 12


def test_filter_by_crop_and_market(client):
    data = client.get("/api/prices?crop=maize&market=kimironko").get_json()
    assert data["count"] == 1
    assert data["prices"][0]["price"] == 450


def test_add_price_success(client):
    res = client.post("/api/prices", json={"crop": "cassava", "market": "huye", "price": 300})
    assert res.status_code == 201
    assert res.get_json()["crop"] == "Cassava"
    assert client.get("/api/prices?crop=cassava").get_json()["count"] == 1


def test_add_price_validation(client):
    assert client.post("/api/prices", json={"crop": "Maize", "market": "X", "price": -5}).status_code == 400
    assert client.post("/api/prices", json={"market": "X", "price": 5}).status_code == 400
    assert client.post("/api/prices", json={"crop": "Maize", "market": "X", "price": "abc"}).status_code == 400
    assert client.post("/api/prices", data="not json").status_code == 400


def test_summary_has_all_crops(client):
    summary = client.get("/api/prices/summary").get_json()["summary"]
    assert {s["crop"] for s in summary} == {"Maize", "Beans", "Tomatoes", "Rice", "Potatoes"}


def test_compare_markets_cheapest_first(client):
    data = client.get("/api/crops/maize/compare").get_json()
    assert data["cheapest_market"] == "Musanze"
    prices = [m["price"] for m in data["markets"]]
    assert prices == sorted(prices)


def test_compare_unknown_crop_404(client):
    assert client.get("/api/crops/unicorn/compare").status_code == 404
