import re
from calendar import monthrange
from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Budget, Category, Transaction

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")

YEAR_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")


def _is_valid_year_month(value):
    if not isinstance(value, str) or not YEAR_MONTH_RE.match(value):
        return False
    year, month = (int(part) for part in value.split("-"))
    return 1 <= month <= 12 and year > 0


def _month_bounds(year_month):
    year, month = (int(part) for part in year_month.split("-"))
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


def _validate_payload(data, *, require_all):
    errors = {}

    if "category_id" in data or require_all:
        category_id = data.get("category_id")
        if Category.query.get(category_id) is None:
            errors["category_id"] = "category not found"

    if "year_month" in data or require_all:
        if not _is_valid_year_month(data.get("year_month")):
            errors["year_month"] = "must be in YYYY-MM format"

    if "amount" in data or require_all:
        try:
            amount = float(data.get("amount"))
            if amount <= 0:
                errors["amount"] = "must be a positive number"
        except (TypeError, ValueError):
            errors["amount"] = "must be a number"

    return errors


def _spent_amount(category_id, year_month):
    start, end = _month_bounds(year_month)
    return (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.category_id == category_id,
            Transaction.type == "expense",
            Transaction.date.between(start, end),
        )
        .scalar()
    )


def _to_dict_with_usage(budget):
    data = budget.to_dict()
    spent = float(_spent_amount(budget.category_id, budget.year_month))
    data["spent"] = spent
    data["remaining"] = data["amount"] - spent
    data["progress"] = round(spent / data["amount"], 4) if data["amount"] else 0.0
    return data


@budgets_bp.get("")
def list_budgets():
    month = request.args.get("month")
    query = Budget.query
    if month:
        if not _is_valid_year_month(month):
            return jsonify(errors={"month": "must be in YYYY-MM format"}), 400
        query = query.filter(Budget.year_month == month)

    budgets = query.order_by(Budget.year_month, Budget.category_id).all()
    return jsonify([_to_dict_with_usage(b) for b in budgets])


@budgets_bp.post("")
def create_budget():
    data = request.get_json(silent=True) or {}
    errors = _validate_payload(data, require_all=True)
    if errors:
        return jsonify(errors=errors), 400

    budget = Budget(
        category_id=data["category_id"],
        year_month=data["year_month"],
        amount=data["amount"],
    )
    db.session.add(budget)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(errors={"budget": "a budget for this category and month already exists"}),
            409,
        )
    return jsonify(_to_dict_with_usage(budget)), 201


@budgets_bp.put("/<int:budget_id>")
def update_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    data = request.get_json(silent=True) or {}
    errors = _validate_payload(data, require_all=False)
    if errors:
        return jsonify(errors=errors), 400

    if "category_id" in data:
        budget.category_id = data["category_id"]
    if "year_month" in data:
        budget.year_month = data["year_month"]
    if "amount" in data:
        budget.amount = data["amount"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(errors={"budget": "a budget for this category and month already exists"}),
            409,
        )
    return jsonify(_to_dict_with_usage(budget))


@budgets_bp.delete("/<int:budget_id>")
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    db.session.delete(budget)
    db.session.commit()
    return "", 204
