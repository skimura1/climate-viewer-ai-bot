from flask import Flask
from app.config import config
from app.extensions import cors
from app.api import register_blueprints


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    cors.init_app(app)

    # Register blueprints
    register_blueprints(app)

    return app
