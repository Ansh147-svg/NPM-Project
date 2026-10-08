"""Common schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 100
    total: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    timestamp: datetime = None