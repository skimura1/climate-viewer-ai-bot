import os
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import logging

from pydantic import ValidationError

from app.models.ai import ChatRequest
from app.services.ai_service import AIService
from app.services.geoserver_service import Geoserver

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
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "service": "climate-viewer-ai-bot",
        }
    )


@api_bp.route("/chat", methods=["POST"])
def chat():
    try:
        chat_request = ChatRequest.model_validate(request.get_json())
        query = chat_request.query
        aiservice = AIService()
        instructions = """
You are a GeoServer layer selection assistant for Hawaii sea level rise and flooding data. Your job is to analyze user requests and select exactly ONE layer with the appropriate foot increment.

AVAILABLE LAYER TEMPLATES:
- Passive GWI ${ft} ft all-scenarios: Statewide 80% probability flooding data

LOCATION COORDINATES:
- Waikiki: {
    north: 21.2830,
    south: 21.2570,
    east: -157.8050,
    west: -157.8350
    }
- Koolaupoko: {
    north: 21.6500,
    south: 21.3090,
    east: -157.6500,
    west: -157.9000
    }

PARAMETERS:
- {ft}: Foot increment from 0-10 (00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10)

RULES:
1. Select exactly ONE layer that best matches the user's request
2. Choose appropriate foot increment (0-10ft) based on user's scenario
3. If no specific footage mentioned, default to 3ft
4. If location is specified, prioritize location-specific layers and return a boundaries for that location
5. Choose the most relevant layer type for the user's interest
6. If location is not specified, set boundaries to null 

OUTPUT FORMAT:
{
  "layer": "complete_layer_name_with_values_filled_in",
  "foot_increment": number,
  "boundaries": "Location of interest boundaries in this format {"north": number, "south": number, "east": number, "west": number}",
  "reason": "Brief explanation of layer and footage choice"
}

EXAMPLES:
User: "Show me 6 foot flooding in Koolaupoko"
Response: {
"layer": "CRC:HI_Oahu_inundation_06ft", 
"foot_increment": 6, 
"boundaries": {
    "north": 21.6500, 
    "south": 21.3090, 
    "east": -157.6500, 
    "west": -157.9000
    },
"reason": "Oahu-specific flooding data at 6 foot level"
}

User: "What areas flood in Waikiki?"
Response: {
"layer": "CRC:Waikiki_compound_prelim_03ft", 
"foot_increment": 3, 
"boundaries": {
    "north": 21.2830,
    "south": 21.2570,
    "east": -157.8050,
    "west": -157.8350
    },
"reason": "Waikiki-specific compound flooding data at default 3ft level"
}
        """

        response = aiservice.get_response(prompt=query, instructions=instructions)

        return response.output_text, 201

    except ValidationError as e:
        # Handle validation errors
        return jsonify({"errors": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @api_bp.route("/geoserver", methods=["GET"])
# def geoserver():
#     try:
#         url = os.getenv("GEOSERVER_URL")
#         username = os.getenv("GEOSERVER_USERNAME")
#         password = os.getenv("GEOSERVER_PASSWORD")
#         assert url is not None, "GEOSERVER_URL must be set in .env"
#         assert username is not None, "GEOSERVER_USERNAME must be set in .env"
#         assert password is not None, "GEOSERVER_PASSWORD must be set in .env"
#
#         geoserver_service = Geoserver(
#             url=url,
#             username=username,
#             password=password,
#         )
#         workspaces = geoserver_service.get_workspaces()
#         return jsonify(workspaces), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
