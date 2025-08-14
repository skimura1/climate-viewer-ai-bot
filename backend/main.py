import json
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from ai.climate_agent import ClimateAgent
from models.chat import ChatRequest

load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

origins = ["http://localhost:3000", "https://localhost:3000",
"http://localhost:5173", "https://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_climate_agent():
    return ClimateAgent()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat", status_code=201)
async def chat(chat_request: ChatRequest, climate_agent: ClimateAgent = Depends(get_climate_agent)):
    try:
        query = chat_request.query
        map_state = chat_request.map_state


        response = await climate_agent.process_query(query=query,
                                               map_state=map_state,
                                               session_id="0")

        return response

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Invalid JSON from AI response", "Details": str(e)},
        ) from e
    except ValidationError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=400,
            detail={"error": "AI response validation failed", "errors": e.errors()},
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errors": str(e)}) from e
