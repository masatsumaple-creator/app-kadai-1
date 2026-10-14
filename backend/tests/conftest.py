import os
import tempfile

import pytest

from app import create_app
from app.extensions import db
from app.models import Category


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".sqlite")
    test_app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "TESTING": True,
        }
    )

    with test_app.app_context():
        db.create_all()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.engine.dispose()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_category(app):
    def _make_category(name="食費", type_="expense"):
        with app.app_context():
            category = Category(name=name, type=type_)
            db.session.add(category)
            db.session.commit()
            return category.id

    return _make_category
