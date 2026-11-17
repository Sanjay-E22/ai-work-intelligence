
import re
from datetime import date, datetime
from typing import Iterable

from app.schemas.workflow import ProcessedTask


DATE_FORMATS = (
    "%Y-%m-%d",
    "%d %B %Y",
    "%d %b %Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
)


def parse_deadline(value: str | None) -> date | None:
    """Parse common date formats returned by the AI extractor."""
    if not value:
        return None

    value = value.strip()

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date()
    except ValueError:
        pass

    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    return None


def calculate_priority(
    deadline: str | None,
    today: date | None = None,
) -> str:
    """Calculate priority using the number of days until the deadline."""
    due_date = parse_deadline(deadline)

    if due_date is None:
        return "unknown"

    today = today or date.today()
    days_remaining = (due_date - today).days

    if days_remaining <= 1:
        return "urgent"
    if days_remaining <= 3:
        return "high"
    if days_remaining <= 7:
        return "medium"

    return "low"


def normalize_dependencies(
    tasks: list,
) -> list[ProcessedTask]:
    """
    Convert references such as 'Task 1' into actual task descriptions.
    Dependency matching is case-insensitive.
    """
    descriptions = [task.description for task in tasks]

    normalized_tasks = []

    for task in tasks:
        normalized_dependencies = []

        for dependency in task.dependencies:
            dependency = dependency.strip()

            # Convert "Task 2" into the second extracted task's description.
            match = re.fullmatch(r"task\s+(\d+)", dependency, re.IGNORECASE)

            if match:
                task_number = int(match.group(1))

                if 1 <= task_number <= len(descriptions):
                    dependency = descriptions[task_number - 1]

            normalized_dependencies.append(dependency)

        task_data = task.model_dump()
        task_data["dependencies"] = normalized_dependencies

        normalized_tasks.append(task_data)

    return [
        ProcessedTask.model_validate(task)
        for task in normalized_tasks
    ]


def calculate_execution_status(
    task: ProcessedTask,
    completed_tasks: Iterable[str] | None = None,
) -> str:
    """A task is blocked until all its dependencies are completed."""
    completed = {
        item.strip().casefold()
        for item in (completed_tasks or [])
    }

    for dependency in task.dependencies:
        if dependency.strip().casefold() not in completed:
            return "blocked"

    return "ready"


def prepare_processed_tasks(
    extracted_tasks: list,
    completed_tasks: Iterable[str] | None = None,
    today: date | None = None,
) -> list[ProcessedTask]:
    """Normalize dependencies and calculate priority and execution status."""
    normalized = normalize_dependencies(extracted_tasks)

    return [
        ProcessedTask.model_validate(
            {
                **task.model_dump(),
                "priority": calculate_priority(task.deadline, today),
                "execution_status": calculate_execution_status(
                    task,
                    completed_tasks,
                ),
            }
        )
        for task in normalized
    ]
