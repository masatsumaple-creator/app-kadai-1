from datetime import date, datetime

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import TRANSACTION_TYPES, Category, Transaction

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _validate_payload(data, *, require_all):
    errors = {}

    if "type" in data or require_all:
        if data.get("type") not in TRANSACTION_TYPES:
            errors["type"] = f"must be one of {TRANSACTION_TYPES}"

    if "amount" in data or require_all:
        try:
            amount = float(data.get("amount"))
            if amount <= 0:
                errors["amount"] = "must be a positive number"
        except (TypeError, ValueError):
            errors["amount"] = "must be a number"

    if "date" in data or require_all:
        if _parse_date(data.get("date")) is None:
            errors["date"] = "must be an ISO date (YYYY-MM-DD)"

    category_id = data.get("category_id")
    if category_id is not None:
        if Category.query.get(category_id) is None:
            errors["category_id"] = "category not found"

    return errors


@transactions_bp.get("")
def list_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    return jsonify([t.to_dict() for t in transactions])


@transactions_bp.post("")
def create_transaction():
    data = request.get_json(silent=True) or {}
    errors = _validate_payload(data, require_all=True)
    if errors:
        return jsonify(errors=errors), 400

    transaction = Transaction(
        category_id=data.get("category_id"),
        type=data["type"],
        amount=data["amount"],
        date=_parse_date(data["date"]),
        memo=data.get("memo"),
        created_at=datetime.utcnow(),
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction.to_dict()), 201


@transactions_bp.put("/<int:transaction_id>")
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    data = request.get_json(silent=True) or {}
    errors = _validate_payload(data, require_all=False)
    if errors:
        return jsonify(errors=errors), 400

    if "type" in data:
        transaction.type = data["type"]
    if "amount" in data:
        transaction.amount = data["amount"]
    if "date" in data:
        transaction.date = _parse_date(data["date"])
    if "memo" in data:
        transaction.memo = data["memo"]
    if "category_id" in data:
        transaction.category_id = data["category_id"]

    db.session.commit()
    return jsonify(transaction.to_dict())


@transactions_bp.delete("/<int:transaction_id>")
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return "", 204
