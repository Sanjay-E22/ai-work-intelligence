
from sqlalchemy.orm import Session

from app.ai.workflow import DocumentWorkflow
from app.db.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.workflow import WorkflowResult


class DocumentService:
    """Coordinate document processing and database persistence."""

    def __init__(
        self,
        db: Session,
        workflow: DocumentWorkflow | None = None,
    ):
        self.workflow = workflow or DocumentWorkflow()
        self.document_repository = DocumentRepository(db)
        self.task_repository = TaskRepository(db)

    def process_document(
        self,
        content: bytes,
        file_type: str,
        filename: str,
    ):
        result = self.workflow.process(
            content=content,
            file_type=file_type,
        )

        document = self.document_repository.create(
            filename=filename,
            file_type=file_type,
            summary=result.summary.summary,
        )

        self.task_repository.create_many(
            document_id=document.id,
            tasks=result.tasks,
        )

        return document, result

    def get_document(self, document_id: int):
        return self.document_repository.get_by_id(document_id)

    def get_documents(self):
        return self.document_repository.get_all()
