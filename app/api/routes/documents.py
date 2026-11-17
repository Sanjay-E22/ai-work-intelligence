
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import (
    DocumentProcessResponse,
    DocumentRecordResponse,
)
from app.services.document_service import DocumentService
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, status

from app.db.models.job import Job
from app.workers.background import process_document_background
router = APIRouter(prefix="/documents", tags=["Documents"])

document_service = DocumentService(Session)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/process", response_model=DocumentProcessResponse,)
def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    WHY: Validate and process an uploaded document.
    ARGS: file - Uploaded PDF or TXT document.
    RETURN: Summary and extracted task information.
    RAISE: HTTPException for invalid uploads or processing errors.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    file_type = file.filename.rsplit(".", 1)[-1].lower()

    if file_type not in {"pdf", "txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported",
        )

    # Read one extra byte to detect files exceeding the limit.
    content = file.file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB",
        )

    if file_type == "pdf":
        if b"%PDF-" not in content[:1024]:
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file content",
            )

    elif file_type == "txt":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail="TXT file must contain valid UTF-8 text",
            ) from e

    service = DocumentService(db)

    try:
        document, result = service.process_document(
            content=content,
            file_type=file_type,
            filename=file.filename,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    return DocumentProcessResponse(
        id=document.id,
        filename=document.filename,
        summary=result.summary,
        tasks=result.tasks,
        total_tasks=len(result.tasks),
    )



@router.get(
    "/",
    response_model=list[DocumentRecordResponse],
)
def get_all_documents(db: Session = Depends(get_db)):
    """Return all saved document records."""
    service = DocumentService(db)
    return service.get_documents()


@router.get(
    "/{document_id}",
    response_model=DocumentRecordResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """Return one saved document by ID."""
    service = DocumentService(db)
    document = service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document



@router.post(
    "/submit",
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Accept a document and schedule background processing."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    file_type = file.filename.rsplit(".", 1)[-1].lower()

    if file_type not in {"pdf", "txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported",
        )

    content = file.file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB",
        )

    if file_type == "pdf" and b"%PDF-" not in content[:1024]:
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file content",
        )

    if file_type == "txt":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="TXT file must contain valid UTF-8 text",
            ) from exc

    upload_dir = Path("storage/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_path = upload_dir / f"{uuid4().hex}.{file_type}"

    try:
        stored_path.write_bytes(content)

        job = Job(
            filename=file.filename,
            file_type=file_type,
            status="pending",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        background_tasks.add_task(
            process_document_background,
            job.id,
            str(stored_path.resolve()),
        )

    except Exception as exc:
        db.rollback()
        stored_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to submit document for processing",
        ) from exc

    return {
        "job_id": job.id,
        "status": job.status,
        "message": "Document accepted for background processing",
    }
