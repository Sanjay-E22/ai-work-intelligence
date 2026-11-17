
from app.schemas.task import ExtractedTask
from app.ai.agents.dependency_manager import get_execution_status


def test_task_is_ready():
    task = ExtractedTask(
        description="Write API documentation",
        dependencies=["Complete database integration"]
    )

    completed = {"Complete database integration"}

    assert get_execution_status(task, completed) == "ready"


def test_task_is_blocked():
    task = ExtractedTask(
        description="Write API documentation",
        dependencies=["Complete database integration"]
    )

    completed = set()

    assert get_execution_status(task, completed) == "blocked"


def test_task_is_completed():
    task = ExtractedTask(
        description="Write API documentation",
        dependencies=["Complete database integration"]
    )

    completed = {"Write API documentation"}

    assert get_execution_status(task, completed) == "completed"


def test_task_without_dependencies():
    task = ExtractedTask(
        description="Create project README",
        dependencies=[]
    )

    assert get_execution_status(task, set()) == "ready"
