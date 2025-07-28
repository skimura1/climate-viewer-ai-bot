from abc import ABC, abstractmethod
from openai import OpenAI
from openai.types.responses.response import Response
from typing import Optional, TypeVar, Generic

T = TypeVar("T")


class AIService(ABC, Generic[T]):
    """Abstract AI Service"""

    @abstractmethod
    def get_response(self, prompt: str, instructions: str) -> Optional[T]:
        pass


class OpenAIService(AIService):
    """Service class for handling calls to AI Endpoint."""

    def __init__(self):
        self.client = OpenAI()

    def get_response(self, prompt: str, instructions: str) -> Optional[Response]:
        response = self.client.responses.create(
            model="gpt-4.1",
            instructions=instructions,
            input=prompt,
        )

        return response
