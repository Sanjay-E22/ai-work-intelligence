
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_type: str
    status: str
    document_id: int | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
