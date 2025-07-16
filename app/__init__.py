from flask import Flask
from app.config import config
from app.extensions import cors
from app.api import register_blueprints
from app.frontend import register_frontend_blueprints


def create_app(config_name="development"):
    app = Flask(__name__, static_folder="../static", static_url_path="")
    app.config.from_object(config[config_name])

    # Initialize extensions
    cors.init_app(app)

    # Register blueprints
    register_blueprints(app)  # API blueprints
    register_frontend_blueprints(app)  # Frontend blueprints

    return app
