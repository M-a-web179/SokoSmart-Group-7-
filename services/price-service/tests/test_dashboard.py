def test_dashboard_serves_html(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.content_type
    body = res.get_data(as_text=True)
    assert "SokoSmart" in body
    assert "dashboard.js" in body
    assert "dashboard.css" in body


def test_dashboard_static_assets(client):
    assert client.get("/static/css/dashboard.css").status_code == 200
    assert client.get("/static/js/dashboard.js").status_code == 200
