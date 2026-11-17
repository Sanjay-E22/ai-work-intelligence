
import pytest

from app.ai.agents.extractor import TaskExtractor


class FakeOllamaClient:
    """Simulate Ollama responses without calling the actual model."""

    def generate_structured(self, prompt: str, schema: dict) -> str:
        return """
        {
            "tasks": [
                {
                    "description": "Complete database migration",
                    "assignee": "Sanjay",
                    "deadline": "Friday",
                    "dependencies": []
                }
            ]
        }
        """


def test_extract_valid_tasks():
    extractor = TaskExtractor(client=FakeOllamaClient())

    result = extractor.extract(
        "Sanjay must complete database migration by Friday."
    )

    assert len(result.tasks) == 1
    assert result.tasks[0].description == "Complete database migration"
    assert result.tasks[0].assignee == "Sanjay"
    assert result.tasks[0].deadline == "Friday"


def test_extract_rejects_empty_document():
    extractor = TaskExtractor(client=FakeOllamaClient())

    with pytest.raises(ValueError, match="Document text cannot be empty"):
        extractor.extract("")


def test_extract_rejects_invalid_json():
    class InvalidClient:
        def generate_structured(self, prompt, schema):
            return "This is not JSON"

    extractor = TaskExtractor(client=InvalidClient())

    with pytest.raises(
        ValueError,
        match="Failed to extract valid structured tasks",
    ):
        extractor.extract("Complete the API integration.")


def test_extract_rejects_invalid_task_structure():
    class InvalidStructureClient:
        def generate_structured(self, prompt, schema):
            return '{"tasks": [{"assignee": "Sanjay"}]}'

    extractor = TaskExtractor(client=InvalidStructureClient())

    with pytest.raises(
        ValueError,
        match="Failed to extract valid structured tasks",
    ):
        extractor.extract("Complete the API integration.")
