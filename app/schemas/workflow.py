
from pydantic import BaseModel

from app.schemas.summary import SummaryResult
from app.schemas.task import ExtractedTask


class ProcessedTask(ExtractedTask):
    """Represent an extracted task with calculated information."""

    priority: str
    execution_status: str


class WorkflowResult(BaseModel):
    """Represent the complete document-processing result."""

    summary: SummaryResult
    tasks: list[ProcessedTask]
