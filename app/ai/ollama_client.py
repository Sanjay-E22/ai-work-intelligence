
import ollama

from app.core.config import settings


class OllamaClient:
    """Provide access to the configured local LLM."""

    def __init__(self) -> None:
        self.client = ollama.Client(
            host=settings.ollama_base_url,
            timeout=300,
        )

    def generate(self, prompt: str) -> str:
        """Generate a normal text response."""
        response = self.client.chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )

        return response.message.content

    def generate_structured(self, prompt: str, schema: dict) -> str:
        """
        WHY: Request model output constrained by a JSON schema.
        ARGS: prompt - extraction instructions; schema - JSON schema.
        RETURN: Generated JSON as a string.
        RAISE: Ollama errors if generation fails.
        """
        response = self.client.chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": prompt}],
            format=schema,
            options={"temperature": 0},
        )

        return response.message.content
