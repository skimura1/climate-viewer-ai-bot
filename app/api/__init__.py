from app.api.routes import api_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(api_bp, url_prefix="/api/v1")
