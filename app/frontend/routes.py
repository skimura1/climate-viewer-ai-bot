from flask import Blueprint, send_from_directory

# Create frontend blueprint
frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.route("/")
def index():
    """Serve the main application page."""
    return send_from_directory("../static", "index.html")
