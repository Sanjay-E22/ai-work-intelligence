
from sqlalchemy.orm import Session

from app.db.models.task import Task
from app.repositories.task_repository import TaskRepository


class TaskService:
    """Handle task-management business operations."""

    VALID_PRIORITIES = {"urgent", "high", "medium", "low", "unknown"}

    VALID_STATUSES = {
        "ready",
        "blocked",
        "completed",
        "in_progress",
    }

    def __init__(self, db: Session):
        self.repository = TaskRepository(db)

    def get_tasks(
        self,
        priority: str | None = None,
        execution_status: str | None = None,
    ) -> list[Task]:

        if priority and priority not in self.VALID_PRIORITIES:
            raise ValueError("Invalid priority")

        if execution_status and execution_status not in self.VALID_STATUSES:
            raise ValueError("Invalid execution status")

        return self.repository.get_all(priority, execution_status)

    def get_task(self, task_id: int) -> Task | None:
        return self.repository.get_by_id(task_id)

    def update_task(self, task_id: int, updates: dict) -> Task | None:
        task = self.repository.get_by_id(task_id)

        if task is None:
            return None

        if "description" in updates and updates["description"] is None:
            raise ValueError("Description cannot be null")

        if "priority" in updates:
            if updates["priority"] not in self.VALID_PRIORITIES:
                raise ValueError("Invalid priority")

        if "execution_status" in updates:
            if updates["execution_status"] not in self.VALID_STATUSES:
                raise ValueError("Invalid execution status")

        return self.repository.update(task, updates)

    def delete_task(self, task_id: int) -> bool:
        task = self.repository.get_by_id(task_id)

        if task is None:
            return False

        self.repository.delete(task)
        return True
