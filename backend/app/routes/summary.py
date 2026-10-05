from calendar import monthrange
from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import extract, func

from ..extensions import db
from ..models import Category, Transaction

summary_bp = Blueprint("summary", __name__, url_prefix="/api/summary")


def _parse_month(value):
    try:
        year, month = (int(part) for part in value.split("-"))
        if not 1 <= month <= 12:
            raise ValueError
        return year, month
    except (AttributeError, ValueError):
        return None


def _month_bounds(year, month):
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


@summary_bp.get("")
def monthly_summary():
    month_param = request.args.get("month")
    parsed = _parse_month(month_param) if month_param else None
    if parsed is None:
        return jsonify(errors={"month": "query parameter is required (YYYY-MM)"}), 400

    year, month = parsed
    start, end = _month_bounds(year, month)
    in_month = Transaction.date.between(start, end)

    income_total = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(in_month, Transaction.type == "income")
        .scalar()
    )
    expense_total = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(in_month, Transaction.type == "expense")
        .scalar()
    )

    by_category_rows = (
        db.session.query(
            Category.id,
            Category.name,
            Category.type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(in_month)
        .group_by(Category.id, Category.name, Category.type)
        .order_by(Category.type, Category.id)
        .all()
    )

    return jsonify(
        {
            "month": month_param,
            "income_total": float(income_total),
            "expense_total": float(expense_total),
            "balance": float(income_total) - float(expense_total),
            "by_category": [
                {
                    "category_id": row.id,
                    "name": row.name,
                    "type": row.type,
                    "total": float(row.total),
                }
                for row in by_category_rows
            ],
        }
    )


@summary_bp.get("/trend")
def monthly_trend():
    year_col = extract("year", Transaction.date)
    month_col = extract("month", Transaction.date)

    rows = (
        db.session.query(
            year_col.label("year"),
            month_col.label("month"),
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .group_by(year_col, month_col, Transaction.type)
        .all()
    )

    months = {}
    for row in rows:
        key = f"{int(row.year):04d}-{int(row.month):02d}"
        entry = months.setdefault(
            key, {"month": key, "income_total": 0.0, "expense_total": 0.0}
        )
        entry[f"{row.type}_total"] = float(row.total)

    for entry in months.values():
        entry["balance"] = entry["income_total"] - entry["expense_total"]

    return jsonify(sorted(months.values(), key=lambda e: e["month"]))
