
from app.schemas.task import ExtractedTask


def get_execution_status(
    task: ExtractedTask,
    completed_tasks: set[str]
) -> str:
    """
    WHY: Determine whether a task is ready to execute.
    ARGS:
        task - Task whose execution status is being checked.
        completed_tasks - Descriptions of completed tasks.
    RETURN: completed, blocked, or ready.
    RAISE: No exception for missing dependencies.
    """

    # A completed task should remain completed,
    # regardless of its dependency status.
    if task.description in completed_tasks:
        return "completed"

    # Check whether any dependency is incomplete.
    for dependency in task.dependencies:
        if dependency not in completed_tasks:
            return "blocked"

    # All dependencies are completed.
    return "ready"
