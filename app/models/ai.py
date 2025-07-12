from typing import List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class ResponseOutputText(BaseModel):
    text: str


class ResponseOutputMessage(BaseModel):
    content: List[ResponseOutputText]


class ChatResponse(BaseModel):
    output: List[ResponseOutputMessage]
