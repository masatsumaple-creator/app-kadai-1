def test_create_and_list_category(client):
    res = client.post("/api/categories", json={"name": "書籍代", "type": "expense"})
    assert res.status_code == 201
    created = res.get_json()
    assert created["name"] == "書籍代"
    assert created["type"] == "expense"

    res = client.get("/api/categories")
    assert res.status_code == 200
    assert [c["name"] for c in res.get_json()] == ["書籍代"]


def test_create_category_validation_error(client):
    res = client.post("/api/categories", json={"name": "", "type": "invalid"})
    assert res.status_code == 400
    body = res.get_json()
    assert "name" in body["errors"]
    assert "type" in body["errors"]


def test_update_category(client, make_category):
    category_id = make_category(name="食費", type_="expense")

    res = client.put(f"/api/categories/{category_id}", json={"name": "食費・外食"})
    assert res.status_code == 200
    assert res.get_json()["name"] == "食費・外食"


def test_delete_category_unassigns_transactions_and_removes_budgets(client, make_category):
    category_id = make_category(name="食費", type_="expense")

    client.post(
        "/api/transactions",
        json={
            "category_id": category_id,
            "type": "expense",
            "amount": 1000,
            "date": "2026-10-01",
            "memo": "test",
        },
    )
    client.post(
        "/api/budgets",
        json={"category_id": category_id, "year_month": "2026-10", "amount": 5000},
    )

    res = client.delete(f"/api/categories/{category_id}")
    assert res.status_code == 204

    transactions = client.get("/api/transactions").get_json()
    assert transactions[0]["category_id"] is None

    budgets = client.get("/api/budgets?month=2026-10").get_json()
    assert budgets == []


def test_delete_nonexistent_category_returns_404(client):
    res = client.delete("/api/categories/9999")
    assert res.status_code == 404
