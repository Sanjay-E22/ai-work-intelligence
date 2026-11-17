
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.job import Job
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve the processing status of a job."""

    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job
