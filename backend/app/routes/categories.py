from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import TRANSACTION_TYPES, Category

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


def _validate_payload(data, *, require_all):
    errors = {}

    if "name" in data or require_all:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            errors["name"] = "must be a non-empty string"

    if "type" in data or require_all:
        if data.get("type") not in TRANSACTION_TYPES:
            errors["type"] = f"must be one of {TRANSACTION_TYPES}"

    return errors


@categories_bp.get("")
def list_categories():
    categories = Category.query.order_by(Category.type, Category.id).all()
    return jsonify([c.to_dict() for c in categories])


@categories_bp.post("")
def create_category():
    data = request.get_json(silent=True) or {}
    errors = _validate_payload(data, require_all=True)
    if errors:
        return jsonify(errors=errors), 400

    category = Category(name=data["name"].strip(), type=data["type"])
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@categories_bp.put("/<int:category_id>")
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json(silent=True) or {}
    errors = _validate_payload(data, require_all=False)
    if errors:
        return jsonify(errors=errors), 400

    if "name" in data:
        category.name = data["name"].strip()
    if "type" in data:
        category.type = data["type"]

    db.session.commit()
    return jsonify(category.to_dict())


@categories_bp.delete("/<int:category_id>")
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Transactions referencing this category become unassigned (category_id=NULL,
    # via the FK's ON DELETE SET NULL); budgets for this category are removed
    # along with it (cascade), since a budget without its category is meaningless.
    db.session.delete(category)
    db.session.commit()
    return "", 204
