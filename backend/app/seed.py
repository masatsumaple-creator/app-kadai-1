import click

from .extensions import db
from .models import Category

DEFAULT_CATEGORIES = [
    ("食費", "expense"),
    ("交通費", "expense"),
    ("住居費", "expense"),
    ("娯楽費", "expense"),
    ("その他", "expense"),
    ("給与", "income"),
    ("その他", "income"),
]


def register_seed_command(app):
    @app.cli.command("seed")
    def seed():
        """Insert default categories if none exist yet."""
        if Category.query.first() is not None:
            click.echo("Categories already exist, skipping seed.")
            return

        for name, type_ in DEFAULT_CATEGORIES:
            db.session.add(Category(name=name, type=type_))
        db.session.commit()
        click.echo(f"Seeded {len(DEFAULT_CATEGORIES)} default categories.")
