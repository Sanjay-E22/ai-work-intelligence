
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task_api import TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    priority: str | None = Query(default=None),
    execution_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = TaskService(db)

    try:
        return service.get_tasks(
            priority=priority,
            execution_status=execution_status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = TaskService(db).get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided",
        )

    try:
        task = TaskService(db).update_task(task_id, updates)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    deleted = TaskService(db).delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return {
        "message": "Task deleted successfully",
        "task_id": task_id,
    }
