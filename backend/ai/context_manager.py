from abc import ABC, abstractmethod
from typing import Dict, Optional
from backend.models.chat import (
    ChatContext,
    MapStateData,
    Message,
)
import datetime


class ContextStore(ABC):
    """Abstract base class for context storage"""

    @abstractmethod
    async def get_context(self, session_id: str) -> Optional[ChatContext]:
        pass

    @abstractmethod
    async def save_context(self, session_id: str, context: ChatContext) -> None:
        pass

    @abstractmethod
    async def add_message(
        self, session_id: str, message: Message, map_state: MapStateData
    ) -> None:
        pass


class InMemoryContextStore(ContextStore):
    """Dictionary Based storage for prototyping"""

    def __init__(self):
        self.contexts: Dict[str, ChatContext] = {}

    async def get_context(self, session_id: str) -> Optional[ChatContext]:
        return self.contexts.get(session_id)

    async def save_context(self, session_id: str, context: ChatContext) -> None:
        self.contexts[session_id] = context

    async def add_message(
        self, session_id: str, message: Message, map_state: MapStateData
    ) -> None:
        if session_id not in self.contexts:
            self.contexts[session_id] = ChatContext(
                session_id=session_id, messages=[], map_state=map_state
            )
            self.contexts[session_id].messages.append(message)


class ContextManager:
    def __init__(self, store: Optional[ContextStore] = None):
        self.store = store or InMemoryContextStore()

    async def get_context(
        self, session_id: str, map_state: MapStateData
    ) -> ChatContext:
        context = await self.store.get_context(session_id)

        if not context:
            context = ChatContext(
                session_id=session_id,
                messages=[],
                map_state=map_state,
            )
            await self.store.save_context(session_id, context)
        return context

    async def update_context(
        self, session_id: str, query: str, response: str, map_state: MapStateData
    ):
        timestamp = str(datetime.datetime.now())
        bot_message = Message(role="BOT", content=response, timestamp=timestamp)
        user_message = Message(role="USER", content=query, timestamp=timestamp)
        await self.store.add_message(
            session_id=session_id, message=bot_message, map_state=map_state
        )
        await self.store.add_message(
            session_id=session_id, message=user_message, map_state=map_state
        )
