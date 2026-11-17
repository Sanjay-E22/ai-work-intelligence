
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.summary import SummaryResult
from app.schemas.workflow import ProcessedTask


class DocumentProcessResponse(BaseModel):
    id: int
    filename: str
    summary: SummaryResult
    tasks: list[ProcessedTask]
    total_tasks: int


class DocumentRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_type: str
    status: str
    summary: str
    created_at: datetime
