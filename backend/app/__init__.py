from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from . import models  # noqa: F401  (ensure models are registered with SQLAlchemy)

    from .routes.health import health_bp
    from .routes.transactions import transactions_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(transactions_bp)

    from .seed import register_seed_command
    register_seed_command(app)

    return app
