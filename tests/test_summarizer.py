
import pytest

from app.ai.agents.summarizer import DocumentSummarizer


class FakeOllamaClient:

    def generate_structured(self, prompt, schema):
        return """
        {
            "summary": "The API integration is delayed.",
            "key_points": [
                "Database migration is incomplete.",
                "Testing is waiting for the updated endpoint."
            ]
        }
        """


def test_summarize_valid_document():
    summarizer = DocumentSummarizer(
        client=FakeOllamaClient()
    )

    result = summarizer.summarize(
        "The API integration is delayed."
    )

    assert result.summary == "The API integration is delayed."
    assert len(result.key_points) == 2


def test_summarize_rejects_empty_document():
    summarizer = DocumentSummarizer(
        client=FakeOllamaClient()
    )

    with pytest.raises(ValueError, match="Document text cannot be empty"):
        summarizer.summarize("")


def test_summarize_rejects_invalid_json():

    class InvalidClient:
        def generate_structured(self, prompt, schema):
            return "Invalid JSON"

    summarizer = DocumentSummarizer(
        client=InvalidClient()
    )

    with pytest.raises(ValueError, match="Failed to generate"):
        summarizer.summarize("Some meeting notes")


def test_summarize_rejects_invalid_schema():

    class InvalidClient:
        def generate_structured(self, prompt, schema):
            return '{"summary": "", "key_points": []}'

    summarizer = DocumentSummarizer(
        client=InvalidClient()
    )

    with pytest.raises(ValueError, match="Failed to generate"):
        summarizer.summarize("Some meeting notes")
