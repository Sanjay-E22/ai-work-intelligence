
from datetime import date, datetime


def get_priority(deadline: str | None, today: date) -> str:
    """
    WHY: Determine task priority using its deadline.
    ARGS:
        deadline - Deadline in supported date formats, or None.
        today - Reference date used for prioritization.
    RETURN: urgent, high, medium, low, or unknown.
    RAISE: No exception for invalid or missing deadlines.
    """
    if not deadline:
        return "unknown"

    supported_formats = [
        "%Y-%m-%d",
        "%d %B %Y",
    ]

    parsed_deadline = None

    for date_format in supported_formats:
        try:
            parsed_deadline = datetime.strptime(
                deadline.strip(), date_format
            ).date()
            break
        except ValueError:
            continue

    if parsed_deadline is None:
        return "unknown"

    remain_days = (parsed_deadline - today).days

    if remain_days <= 0:
        return "urgent"
    elif remain_days <= 3:
        return "high"
    elif remain_days <= 7:
        return "medium"
    else:
        return "low"
