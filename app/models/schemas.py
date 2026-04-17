from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AnalysisResponse(BaseModel):
    sector: str
    session_id: str
    generated_at: datetime
    report_markdown: str
    sources_used: int

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class SessionInfo(BaseModel):
    session_id: str
    request_count: int
    created_at: datetime
    last_request: datetime
