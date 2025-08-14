import datetime
from abc import ABC, abstractmethod

from models.chat import (
    ChatContext,
    Message,
)


class ContextStore(ABC):
    """Abstract base class for context storage"""

    @abstractmethod
    async def get_context(self, session_id: str) -> ChatContext | None:
        pass

    @abstractmethod
    async def save_context(self, session_id: str, context: ChatContext) -> None:
        pass

    @abstractmethod
    async def add_message(self, session_id: str, message: Message) -> None:
        pass


class InMemoryContextStore(ContextStore):
    """Dictionary Based storage for prototyping"""

    def __init__(self):
        self.contexts: dict[str, ChatContext] = {}

    async def get_context(self, session_id: str) -> ChatContext | None:
        return self.contexts.get(session_id)

    async def save_context(self, session_id: str, context: ChatContext) -> None:
        self.contexts[session_id] = context

    async def add_message(self, session_id: str, message: Message) -> None:
        if session_id not in self.contexts:
            self.contexts[session_id] = ChatContext(session_id=session_id, messages=[])
            self.contexts[session_id].messages.append(message)


class ContextManager:
    def __init__(self, store: ContextStore | None = None):
        self.store = store or InMemoryContextStore()

    async def get_context(self, session_id: str) -> ChatContext:
        context = await self.store.get_context(session_id)

        if not context:
            context = ChatContext(
                session_id=session_id,
                messages=[],
            )
            await self.store.save_context(session_id, context)
        return context

    async def update_context(self, session_id: str, query: str, response: str):
        timestamp = str(datetime.datetime.now())
        bot_message = Message(id="0", role="BOT", content=response, timestamp=timestamp)
        user_message = Message(id="1", role="USER", content=query, timestamp=timestamp)
        await self.store.add_message(session_id=session_id, message=bot_message)
        await self.store.add_message(session_id=session_id, message=user_message)
