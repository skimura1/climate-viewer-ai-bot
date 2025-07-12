from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

from pydantic import ValidationError

from app.models.ai import ChatRequest
from app.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint and service instance
api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "climate-viewer-ai-bot",
        }
    )


@api_bp.route("/chat", methods=["POST"])
def chat():
    try:
        chat_request = ChatRequest.model_validate(request.get_json())
        query = chat_request.query
        aiservice = AIService()

        response = aiservice.get_response(prompt=query)

        return response.output_text, 201

    except ValidationError as e:
        # Handle validation errors
        return jsonify({"errors": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
