"""
Models package for Climate Viewer AI Bot.

This package contains data models used throughout the application:
- Pydantic models for API requests/responses (chat.py)
- SQLAlchemy models for database entities (document_chunk.py)
"""

from .chat import (
    ChatContext,
    ChatRequest,
    ChatResponse,
    MapBounds,
    MapCenter,
    MapState,
    Message,
)
from .document_chunk import Base, DocumentChunk

__all__ = [
    # Chat models
    "ChatContext",
    "ChatRequest",
    "ChatResponse",
    "MapBounds",
    "MapCenter",
    "MapState",
    "Message",
    # Database models
    "Base",
    "DocumentChunk",
]
