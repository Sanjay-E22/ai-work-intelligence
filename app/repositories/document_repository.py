
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.document import Document


class DocumentRepository:
    """Handle database operations for documents."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        filename: str,
        file_type: str,
        summary: str,
    ) -> Document:
        """
        WHY: Store a successfully processed document.
        ARGS: filename, file_type, summary.
        RETURN: Newly created document record.
        RAISE: SQLAlchemy errors if database operations fail.
        """
        document = Document(
            filename=filename,
            file_type=file_type,
            summary=summary,
            status="completed",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def get_by_id(self, document_id: int) -> Document | None:
        """Retrieve one document using its ID."""
        statement = select(Document).where(
            Document.id == document_id
        )
        return self.db.scalar(statement)

    def get_all(self) -> list[Document]:
        """Retrieve all documents, newest first."""
        statement = (
            select(Document)
            .order_by(Document.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
