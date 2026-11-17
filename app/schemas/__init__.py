
from pydantic import BaseModel, Field


class ExtractedTask(BaseModel):
    """Represent one task extracted from a document."""

    description: str = Field(min_length=1)
    assignee: str | None = None
    deadline: str | None = None
    dependencies: list[str] = Field(default_factory=list)


class TaskExtractionResult(BaseModel):
    """Represent all tasks extracted from a document."""

    tasks: list[ExtractedTask] = Field(default_factory=list)
