
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.task import Task


class TaskRepository:
    """Handle database operations for tasks."""

    def __init__(self, db: Session):
        self.db = db

    def create_many(self, document_id: int, tasks: list) -> list[Task]:
        """Save extracted tasks belonging to a document."""

        records = [
            Task(
                document_id=document_id,
                description=task.description,
                assignee=task.assignee,
                deadline=task.deadline,
                dependencies=task.dependencies,
                priority=task.priority,
                execution_status=task.execution_status,
            )
            for task in tasks
        ]

        if records:
            self.db.add_all(records)
            self.db.commit()

            for record in records:
                self.db.refresh(record)

        return records

    def get_all(
        self,
        priority: str | None = None,
        execution_status: str | None = None,
    ) -> list[Task]:
        """Retrieve tasks with optional filters."""

        statement = select(Task).order_by(Task.created_at.desc())

        if priority:
            statement = statement.where(Task.priority == priority)

        if execution_status:
            statement = statement.where(
                Task.execution_status == execution_status
            )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, task_id: int) -> Task | None:
        """Retrieve one task by ID."""

        return self.db.get(Task, task_id)

    def update(self, task: Task, updates: dict) -> Task:
        """Update supplied task fields."""

        for field, value in updates.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)

        return task

    def delete(self, task: Task) -> None:
        """Delete a task."""

        self.db.delete(task)
        self.db.commit()
