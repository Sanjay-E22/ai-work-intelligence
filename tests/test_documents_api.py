
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.documents import document_service
from app.schemas.workflow import WorkflowResult
from app.schemas.summary import SummaryResult


client = TestClient(app)


def fake_process_document(content: bytes, file_type: str):
    return WorkflowResult(
        summary=SummaryResult(
            summary="Test document summary",
            key_points=["Project planning"],
        ),
        tasks=[],
    )


def test_upload_valid_txt(monkeypatch):
    monkeypatch.setattr(
        document_service,
        "process_document",
        fake_process_document,
    )

    response = client.post(
        "/documents/process",
        files={
            "file": (
                "meeting.txt",
                b"Complete project planning",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "meeting.txt"
    assert response.json()["total_tasks"] == 0


def test_reject_unsupported_file():
    response = client.post(
        "/documents/process",
        files={
            "file": (
                "meeting.docx",
                b"some content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400


def test_reject_empty_file():
    response = client.post(
        "/documents/process",
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_reject_oversized_file():
    response = client.post(
        "/documents/process",
        files={
            "file": (
                "large.txt",
                b"A" * (10 * 1024 * 1024 + 1),
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
