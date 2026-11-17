
from datetime import date

from app.schemas.task import ExtractedTask
from app.utils.task_normalizer import (
    calculate_priority,
    parse_deadline,
    prepare_processed_tasks,
)


def test_parse_long_date():
    assert parse_deadline("03 November 2026") == date(2026, 11, 3)


def test_parse_iso_date():
    assert parse_deadline("2026-11-03") == date(2026, 11, 3)


def test_invalid_date():
    assert parse_deadline("not a date") is None


def test_priority_calculation():
    today = date(2026, 11, 12)

    assert calculate_priority("2026-11-12", today) == "urgent"
    assert calculate_priority("2026-11-14", today) == "high"
    assert calculate_priority("2026-11-17", today) == "medium"
    assert calculate_priority("2026-11-25", today) == "low"


def test_task_number_dependency_normalization():
    extracted = [
        ExtractedTask(
            description="Prepare project report",
            dependencies=[],
        ),
        ExtractedTask(
            description="Review project report",
            dependencies=["Task 1"],
        ),
    ]

    tasks = prepare_processed_tasks(
        extracted_tasks=extracted,
        today=date(2026, 11, 12),
    )

    assert tasks[1].dependencies == ["Prepare project report"]
    assert tasks[0].execution_status == "ready"
    assert tasks[1].execution_status == "blocked"


def test_completed_dependency_unblocks_task():
    extracted = [
        ExtractedTask(
            description="Prepare project report",
            dependencies=[],
        ),
        ExtractedTask(
            description="Review project report",
            dependencies=["Task 1"],
        ),
    ]

    tasks = prepare_processed_tasks(
        extracted_tasks=extracted,
        completed_tasks=["Prepare project report"],
        today=date(2026, 11, 12),
    )

    assert tasks[1].execution_status == "ready"
