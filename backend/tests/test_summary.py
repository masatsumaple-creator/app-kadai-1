def create_tx(client, **overrides):
    payload = {
        "category_id": None,
        "type": "expense",
        "amount": 1000,
        "date": "2026-10-01",
        "memo": "test",
    }
    payload.update(overrides)
    return client.post("/api/transactions", json=payload)


def test_monthly_summary(client, make_category):
    food = make_category(name="食費", type_="expense")
    salary = make_category(name="給与", type_="income")

    create_tx(client, category_id=salary, type="income", amount=300000, date="2026-10-01")
    create_tx(client, category_id=food, type="expense", amount=15000, date="2026-10-02")
    create_tx(client, category_id=food, type="expense", amount=5000, date="2026-09-20")

    res = client.get("/api/summary?month=2026-10")
    assert res.status_code == 200
    body = res.get_json()
    assert body["income_total"] == 300000.0
    assert body["expense_total"] == 15000.0
    assert body["balance"] == 285000.0
    assert len(body["by_category"]) == 2


def test_summary_requires_month_param(client):
    res = client.get("/api/summary")
    assert res.status_code == 400


def test_monthly_trend(client, make_category):
    food = make_category(name="食費", type_="expense")
    salary = make_category(name="給与", type_="income")

    create_tx(client, category_id=salary, type="income", amount=300000, date="2026-10-01")
    create_tx(client, category_id=food, type="expense", amount=15000, date="2026-10-02")
    create_tx(client, category_id=food, type="expense", amount=20000, date="2026-09-05")

    res = client.get("/api/summary/trend")
    assert res.status_code == 200
    body = res.get_json()
    assert [m["month"] for m in body] == ["2026-09", "2026-10"]
    sept, oct_ = body
    assert sept["expense_total"] == 20000.0
    assert oct_["income_total"] == 300000.0
    assert oct_["balance"] == 285000.0
