from datetime import datetime

from .extensions import db

TRANSACTION_TYPES = ("income", "expense")


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(*TRANSACTION_TYPES, name="category_type"), nullable=False)

    transactions = db.relationship(
        "Transaction", back_populates="category", passive_deletes=True
    )
    budgets = db.relationship(
        "Budget", back_populates="category", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "type": self.type}


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL")
    )
    type = db.Column(db.Enum(*TRANSACTION_TYPES, name="transaction_type"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    memo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    category = db.relationship("Category", back_populates="transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "type": self.type,
            "amount": float(self.amount),
            "date": self.date.isoformat(),
            "memo": self.memo,
            "created_at": self.created_at.isoformat(),
        }


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    year_month = db.Column(db.String(7), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    category = db.relationship("Category", back_populates="budgets")

    __table_args__ = (
        db.UniqueConstraint("category_id", "year_month", name="uq_budget_category_month"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "year_month": self.year_month,
            "amount": float(self.amount),
        }
