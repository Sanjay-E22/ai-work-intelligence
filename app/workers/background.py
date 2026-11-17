
from pathlib import Path

from app.db.session import SessionLocal
from app.db.models.job import Job
from app.services.document_service import DocumentService
import logging

logger = logging.getLogger(__name__)

def process_document_background(
    job_id: int,
    file_path: str,
):
    """
    WHY: Process an uploaded document after the HTTP response.
    ARGS: job_id - Database job ID; file_path - Stored upload path.
    RETURN: None.
    RAISE: Processing errors are recorded in the job.
    """
    path = Path(file_path)
    db = SessionLocal()

    try:
        job = db.get(Job, job_id)
        logger.info("Starting background job %s", job_id)
        if job is None:
            return

        job.status = "processing"
        db.commit()

        content = path.read_bytes()

        service = DocumentService(db)

        document, result = service.process_document(
            content=content,
            file_type=job.file_type,
            filename=job.filename,
        )

        job = db.get(Job, job_id)
        job.document_id = document.id
        job.status = "completed"
        job.error_message = None
        logger.info(
                "Job %s completed. Document ID: %s",
                job_id,
                job.document_id,
            )
        db.commit()

    except Exception as exc:
        db.rollback()

        job = db.get(Job, job_id)
        logger.exception("Background job %s failed", job_id)
        if job is not None:
            job.status = "failed"
            job.error_message = str(exc)[:2000]
            db.commit()

    finally:
        path.unlink(missing_ok=True)
        db.close()
