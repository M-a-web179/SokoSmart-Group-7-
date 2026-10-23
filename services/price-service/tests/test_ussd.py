def ussd(client, text=""):
    res = client.post("/ussd", data={"text": text})
    assert res.status_code == 200
    assert res.content_type.startswith("text/plain")
    return res.get_data(as_text=True)


def test_main_menu_is_level_1(client):
    body = ussd(client)
    assert body.startswith("CON ")
    for option in ("1. Check crop prices", "2. Compare markets", "3. Price summary", "4. Report a price"):
        assert option in body


def test_crop_menu_is_level_2(client):
    body = ussd(client, "1")
    assert body.startswith("CON ")
    assert "Maize" in body
    assert "Beans" in body


def test_prices_for_crop_is_level_3(client):
    body = ussd(client, "1*1")
    assert body.startswith("END ")
    assert "Beans" in body
    assert "RWF/kg" in body


def test_compare_cheapest_first(client):
    body = ussd(client, "2*2")
    assert body.startswith("END ")
    assert "cheapest in Musanze" in body
    lines = body.splitlines()[1:]
    prices = [float(line.split(": ")[1].split(" ")[0]) for line in lines if ": " in line]
    assert prices == sorted(prices)


def test_summary_lists_all_crops(client):
    body = ussd(client, "3")
    assert body.startswith("END ")
    for crop in ("Maize", "Beans", "Rice", "Tomatoes", "Potatoes"):
        assert crop in body


def test_report_price_flow_saves_entry(client):
    assert ussd(client, "4").startswith("CON ")
    assert ussd(client, "4*onion").startswith("CON ")
    assert ussd(client, "4*onion*nyabugogo").startswith("CON ")
    body = ussd(client, "4*onion*nyabugogo*350")
    assert body.startswith("END ")
    assert "Onion" in body and "Nyabugogo" in body and "350" in body
    assert client.get("/api/prices?crop=onion").get_json()["count"] == 1


def test_report_price_invalid_input(client):
    body = ussd(client, "4*onion*nyabugogo*free")
    assert body.startswith("END ")
    assert "Could not save" in body


def test_back_navigation(client):
    assert "Select a crop" in ussd(client, "1")
    assert "Welcome to SokoSmart" in ussd(client, "1*00")


def test_exit_and_invalid_choice(client):
    assert ussd(client, "0").startswith("END ")
    assert ussd(client, "9").startswith("END ")
    assert "Invalid" in ussd(client, "9")
