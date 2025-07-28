from pydantic import BaseModel


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


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatContext(BaseModel):
    session_id: str
    messages: list[Message]
    map_bounds: str
    active_layers: list[str]
