import csv
import io
from datetime import date, datetime

from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models import TRANSACTION_TYPES, Category, Transaction

transactions_io_bp = Blueprint("transactions_io", __name__, url_prefix="/api/transactions")

CSV_COLUMNS = ["date", "type", "category", "amount", "memo"]


@transactions_io_bp.get("/export")
def export_transactions():
    transactions = Transaction.query.order_by(Transaction.date, Transaction.id).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    for t in transactions:
        writer.writerow(
            [
                t.date.isoformat(),
                t.type,
                t.category.name if t.category else "",
                t.amount,
                t.memo or "",
            ]
        )

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


def _parse_row(row, line_number):
    errors = {}

    row_date = None
    try:
        row_date = date.fromisoformat((row.get("date") or "").strip())
    except ValueError:
        errors["date"] = "must be an ISO date (YYYY-MM-DD)"

    row_type = (row.get("type") or "").strip()
    if row_type not in TRANSACTION_TYPES:
        errors["type"] = f"must be one of {TRANSACTION_TYPES}"

    category = None
    category_name = (row.get("category") or "").strip()
    if category_name:
        category = Category.query.filter_by(name=category_name, type=row_type).first()
        if category is None:
            errors["category"] = f"category '{category_name}' ({row_type}) not found"

    try:
        amount = float(row.get("amount"))
        if amount <= 0:
            errors["amount"] = "must be a positive number"
    except (TypeError, ValueError):
        amount = None
        errors["amount"] = "must be a number"

    if errors:
        return None, {"line": line_number, "errors": errors}

    return (
        Transaction(
            category_id=category.id if category else None,
            type=row_type,
            amount=amount,
            date=row_date,
            memo=(row.get("memo") or "").strip() or None,
            created_at=datetime.utcnow(),
        ),
        None,
    )


@transactions_io_bp.post("/import")
def import_transactions():
    uploaded = request.files.get("file")
    if uploaded is None:
        return jsonify(errors={"file": "a CSV file is required (multipart field 'file')"}), 400

    try:
        text = uploaded.stream.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return jsonify(errors={"file": "must be UTF-8 encoded"}), 400

    reader = csv.DictReader(io.StringIO(text))
    missing_columns = set(CSV_COLUMNS) - set(reader.fieldnames or [])
    if missing_columns:
        return jsonify(errors={"file": f"missing columns: {sorted(missing_columns)}"}), 400

    to_insert = []
    row_errors = []
    for line_number, row in enumerate(reader, start=2):  # header is line 1
        transaction, error = _parse_row(row, line_number)
        if error:
            row_errors.append(error)
        else:
            to_insert.append(transaction)

    if to_insert:
        db.session.add_all(to_insert)
        db.session.commit()

    return jsonify(imported=len(to_insert), failed=len(row_errors), errors=row_errors), 201 if to_insert else 200
