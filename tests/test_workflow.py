
from datetime import date

from app.ai.workflow import DocumentWorkflow
from app.schemas.summary import SummaryResult
from app.schemas.task import ExtractedTask, TaskExtractionResult


class FakeSummarizer:
    def summarize(self, document_text):
        return SummaryResult(
            summary="Project API development",
            key_points=["Complete database integration"],
        )


class FakeExtractor:
    def extract(self, document_text):
        return TaskExtractionResult(
            tasks=[
                ExtractedTask(
                    description="Complete database integration",
                    deadline="2026-11-02",
                    dependencies=[],
                ),
                ExtractedTask(
                    description="Write API documentation",
                    deadline="2026-11-05",
                    dependencies=["Complete database integration"],
                ),
            ]
        )


def test_document_workflow():
    workflow = DocumentWorkflow(
        extractor=FakeExtractor(),
        summarizer=FakeSummarizer(),
    )

    result = workflow.process(
        content=b"Complete database integration. Write API documentation.",
        file_type="txt",
        today=date(2026, 10, 31),
    )

    assert result.summary.summary == "Project API development"
    assert len(result.tasks) == 2

    assert result.tasks[0].priority == "high"
    assert result.tasks[0].execution_status == "ready"

    assert result.tasks[1].priority == "medium"
    assert result.tasks[1].execution_status == "blocked"


def test_workflow_with_completed_dependency():
    workflow = DocumentWorkflow(
        extractor=FakeExtractor(),
        summarizer=FakeSummarizer(),
    )

    result = workflow.process(
        content=b"Project tasks",
        file_type="txt",
        today=date(2026, 10, 31),
        completed_tasks={"Complete database integration"},
    )

    assert result.tasks[1].execution_status == "ready"


def test_workflow_rejects_unsupported_file_type():
    workflow = DocumentWorkflow(
        extractor=FakeExtractor(),
        summarizer=FakeSummarizer(),
    )

    try:
        workflow.process(
            content=b"Project tasks",
            file_type="docx",
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "Unsupported file type" in str(error)
