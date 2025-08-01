from typing import Any

from pydantic import BaseModel


class MapBounds(BaseModel):
    north: float
    south: float
    east: float
    west: float
    zoom: int


class MapState(BaseModel):
    active_layers: list[str]
    center: dict[str, float]
    foot_increment: str
    current_map_position: MapBounds


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatContext(BaseModel):
    session_id: str
    messages: list[Message]


class ChatRequest(BaseModel):
    query: str
    map_state: MapState


class ChatResponse(BaseModel):
    response: str
    map_actions: list[dict[str, Any]] | None = None
