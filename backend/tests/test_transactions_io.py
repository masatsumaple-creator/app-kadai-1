import io


def test_export_csv(client, make_category):
    category_id = make_category(name="食費", type_="expense")
    client.post(
        "/api/transactions",
        json={
            "category_id": category_id,
            "type": "expense",
            "amount": 1500,
            "date": "2026-10-02",
            "memo": "スーパー",
        },
    )

    res = client.get("/api/transactions/export")
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    body = res.get_data(as_text=True)
    assert "date,type,category,amount,memo" in body
    assert "2026-10-02,expense,食費,1500.00,スーパー" in body


def test_import_csv_partial_success(client, make_category):
    make_category(name="交通費", type_="expense")

    csv_content = (
        "date,type,category,amount,memo\n"
        "2026-10-05,expense,交通費,800,電車\n"
        "2026-10-06,expense,存在しないカテゴリ,500,謎\n"
        "2026-13-01,expense,交通費,100,不正な日付\n"
        "2026-10-07,expense,交通費,-100,負の金額\n"
    )

    res = client.post(
        "/api/transactions/import",
        data={"file": (io.BytesIO(csv_content.encode("utf-8")), "import.csv")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["imported"] == 1
    assert body["failed"] == 3

    transactions = client.get("/api/transactions").get_json()
    assert len(transactions) == 1
    assert transactions[0]["memo"] == "電車"


def test_import_csv_missing_columns_returns_400(client):
    csv_content = "date,amount\n2026-10-01,100\n"
    res = client.post(
        "/api/transactions/import",
        data={"file": (io.BytesIO(csv_content.encode("utf-8")), "bad.csv")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 400


def test_import_without_file_returns_400(client):
    res = client.post("/api/transactions/import", data={}, content_type="multipart/form-data")
    assert res.status_code == 400
