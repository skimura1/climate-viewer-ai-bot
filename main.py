import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from openai.types.responses.response import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

origins = ["http://localhost:4000", "https://localhost:4000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AIService:
    """Service class for handling calls to AI Endpoint."""

    def __init__(self):
        self.client = OpenAI()

    def get_response(self, prompt: str, instructions: str) -> Response:
        response = self.client.responses.create(
            model="gpt-4.1",
            instructions=instructions,
            input=prompt,
        )

        return response


class ChatRequest(BaseModel):
    query: str


class Boundaries(BaseModel):
    north: float
    south: float
    east: float
    west: float


class LayerData(BaseModel):
    layer: str
    foot_increment: str
    boundaries: Boundaries
    reason: str


class ChatResponse(BaseModel):
    data: LayerData


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat", status_code=201)
def chat(chat_request: ChatRequest):
    try:
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
  "foot_increment": string,
  "boundaries": "Location of interest boundaries in this format {"north": number, "south": number, "east": number, "west": number}",
  "reason": "Brief explanation of layer and footage choice"
}

EXAMPLES:
User: "Show me 6 foot flooding in Koolaupoko"
Response: {
"layer": "CRC:HI_Oahu_inundation_06ft", 
"foot_increment": "6", 
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
"foot_increment": "3", 
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

        raw_message = response.output_text

        parsed_data = json.loads(raw_message)

        validated_data = LayerData.model_validate(parsed_data)

        return ChatResponse(data=validated_data)

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Invalid JSON from AI response", "Details": str(e)},
        )
    except ValidationError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=400,
            detail={"error": "AI response validation failed", "errors": e.errors()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errors": str(e)})
