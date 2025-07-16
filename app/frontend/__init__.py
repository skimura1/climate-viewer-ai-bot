from app.frontend.routes import frontend_bp


def register_frontend_blueprints(app):
    """Register all frontend blueprints with the Flask app."""
    app.register_blueprint(frontend_bp) 