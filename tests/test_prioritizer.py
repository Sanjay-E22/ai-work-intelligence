from datetime import date
from app.ai.agents.prioritizer import get_priority

TODAY = date(2026, 10, 31)


def test_overdue_deadline():
    assert get_priority("2026-10-29", TODAY) == "urgent"


def test_today_deadline():
    assert get_priority("2026-10-31", TODAY) == "urgent"


def test_high_priority():
    assert get_priority("2026-11-02", TODAY) == "high"


def test_medium_priority():
    assert get_priority("2026-11-05", TODAY) == "medium"


def test_low_priority():
    assert get_priority("2026-11-15", TODAY) == "low"


def test_missing_deadline():
    assert get_priority(None, TODAY) == "unknown"


def test_invalid_deadline():
    assert get_priority("Friday", TODAY) == "unknown"