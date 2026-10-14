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


def test_create_list_update_delete_transaction(client, make_category):
    category_id = make_category(name="食費", type_="expense")

    res = create_tx(client, category_id=category_id, amount=1500, memo="スーパー")
    assert res.status_code == 201
    tx_id = res.get_json()["id"]

    res = client.get("/api/transactions")
    assert res.status_code == 200
    assert len(res.get_json()) == 1

    res = client.put(f"/api/transactions/{tx_id}", json={"amount": 2000, "memo": "コンビニ"})
    assert res.status_code == 200
    updated = res.get_json()
    assert updated["amount"] == 2000.0
    assert updated["memo"] == "コンビニ"

    res = client.delete(f"/api/transactions/{tx_id}")
    assert res.status_code == 204
    assert client.get("/api/transactions").get_json() == []


def test_create_transaction_validation_errors(client):
    res = create_tx(client, type="invalid", amount=-5, date="not-a-date")
    assert res.status_code == 400
    errors = res.get_json()["errors"]
    assert "type" in errors
    assert "amount" in errors
    assert "date" in errors


def test_create_transaction_with_unknown_category_fails(client):
    res = create_tx(client, category_id=9999)
    assert res.status_code == 400
    assert "category_id" in res.get_json()["errors"]


def test_delete_nonexistent_transaction_returns_404(client):
    res = client.delete("/api/transactions/9999")
    assert res.status_code == 404


def test_filters(client, make_category):
    food = make_category(name="食費", type_="expense")
    transport = make_category(name="交通費", type_="expense")
    salary = make_category(name="給与", type_="income")

    create_tx(client, category_id=food, type="expense", amount=15000, date="2026-10-02", memo="スーパーで買い物")
    create_tx(client, category_id=transport, type="expense", amount=8000, date="2026-10-15", memo="電車")
    create_tx(client, category_id=salary, type="income", amount=300000, date="2026-10-01", memo="給料")
    create_tx(client, category_id=food, type="expense", amount=5000, date="2026-09-20", memo="スーパー9月")

    res = client.get(f"/api/transactions?category_id={food}")
    assert len(res.get_json()) == 2

    res = client.get("/api/transactions?from=2026-10-01&to=2026-10-31")
    assert len(res.get_json()) == 3

    res = client.get("/api/transactions?type=income")
    assert len(res.get_json()) == 1

    res = client.get("/api/transactions?keyword=%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC")
    assert len(res.get_json()) == 2


def test_filter_invalid_type_returns_400(client):
    res = client.get("/api/transactions?type=invalid")
    assert res.status_code == 400


def test_filter_invalid_date_returns_400(client):
    res = client.get("/api/transactions?from=not-a-date")
    assert res.status_code == 400
