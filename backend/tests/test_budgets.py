def test_create_budget_with_usage(client, make_category):
    category_id = make_category(name="食費", type_="expense")
    client.post(
        "/api/transactions",
        json={
            "category_id": category_id,
            "type": "expense",
            "amount": 15000,
            "date": "2026-10-02",
            "memo": "スーパー",
        },
    )

    res = client.post(
        "/api/budgets", json={"category_id": category_id, "year_month": "2026-10", "amount": 30000}
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["spent"] == 15000.0
    assert body["remaining"] == 15000.0
    assert body["progress"] == 0.5


def test_duplicate_budget_returns_409(client, make_category):
    category_id = make_category(name="食費", type_="expense")
    payload = {"category_id": category_id, "year_month": "2026-10", "amount": 30000}

    assert client.post("/api/budgets", json=payload).status_code == 201
    res = client.post("/api/budgets", json=payload)
    assert res.status_code == 409


def test_budget_with_unknown_category_returns_400(client):
    res = client.post(
        "/api/budgets", json={"category_id": 9999, "year_month": "2026-10", "amount": 1000}
    )
    assert res.status_code == 400


def test_update_and_delete_budget(client, make_category):
    category_id = make_category(name="食費", type_="expense")
    res = client.post(
        "/api/budgets", json={"category_id": category_id, "year_month": "2026-10", "amount": 30000}
    )
    budget_id = res.get_json()["id"]

    res = client.put(f"/api/budgets/{budget_id}", json={"amount": 20000})
    assert res.status_code == 200
    assert res.get_json()["amount"] == 20000.0

    res = client.delete(f"/api/budgets/{budget_id}")
    assert res.status_code == 204
    assert client.get("/api/budgets?month=2026-10").get_json() == []
