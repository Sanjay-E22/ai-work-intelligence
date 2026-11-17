
from pydantic import BaseModel, Field


class SummaryResult(BaseModel):
    """Represent a structured document summary."""

    summary: str = Field(min_length=1)

    key_points: list[str] = Field(
        default_factory=list
    )
