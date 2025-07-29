from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class Boundaries(BaseModel):
    north: float
    south: float
    east: float
    west: float


class MapStateData(BaseModel):
    active_layers: list[str]
    foot_increment: str
    current_map_position: Boundaries


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatContext(BaseModel):
    session_id: str
    messages: list[Message]
    map_state: MapStateData
