import logging

from openai import OpenAI
from openai.types.responses.response import Response


class AIService:
    """Service class for handling calls to OpenAI endpoint."""

    def __init__(self):
        self.client = OpenAI()

    def get_response(self, prompt: str, instructions: str) -> Response:
        response = self.client.responses.create(
            model="gpt-4.1",
            instructions=instructions,
            input=prompt,
        )

        return response
