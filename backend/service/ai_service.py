from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from ollama import Client

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

    def get_response(self, prompt: str) -> ChatCompletion:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response

class OllamaService(AIService):
    """Service class for handling calls to Ollama."""

    def __init__(self):
        self.client = Client()

    def get_response(self, prompt: str) -> str:
        response = self.client.chat(model="qwen3.4b", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]