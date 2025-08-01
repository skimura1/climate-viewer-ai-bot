from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from openai import OpenAI
from openai.types.responses.response import Response

T = TypeVar("T")


class AIService(ABC, Generic[T]):
    """Abstract AI Service"""

    @abstractmethod
    def get_response(self, prompt: str) -> T | None:
        pass


class OpenAIService(AIService):
    """Service class for handling calls to AI Endpoint."""

    def __init__(self):
        self.client = OpenAI()

    def get_response(self, prompt: str) -> Response:
        response = self.client.responses.create(
            model="gpt-4.1",
            input=prompt,
        )

        return response
