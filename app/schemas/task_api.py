
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    description: str
    assignee: str | None
    deadline: str | None
    dependencies: list[str]
    priority: str
    execution_status: str
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1)
    assignee: str | None = None
    deadline: str | None = None
    dependencies: list[str] | None = None
    priority: str | None = None
    execution_status: str | None = None
