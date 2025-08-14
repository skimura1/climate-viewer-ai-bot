from typing import Any

from pydantic import BaseModel


class MapBounds(BaseModel):
    southwest: list[float]
    northeast: list[float]

class MapCenter(BaseModel):
    lat: float
    long: float

class MapState(BaseModel):
    active_layers: list[str] | None
    available_layers: list[str] | None
    foot_increment: str
    map_position: MapBounds
    zoom_level: int
    basemap_name: str
    available_basemaps: list[str]


class Message(BaseModel):
    id: str
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
