from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)

    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    return app
