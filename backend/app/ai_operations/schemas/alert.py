"""
Pydantic schemas for alert data
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AlertBase(BaseModel):
    alert_id: str = Field(..., example="alert-123")
    alert_name: str = Field(..., example="High CPU Usage")
    severity: str = Field(..., example="critical")
    description: str = Field(..., example="CPU usage exceeded 95% for 5 minutes")
    timestamp: Optional[datetime] = Field(None, example="2026-10-07T16:44:23Z")


class AlertCreate(AlertBase):
    pass


class AlertInDBBase(AlertBase):
    id: int
    
    class Config:
        orm_mode = True


class AlertExplanationRequest(BaseModel):
    alert: AlertBase
    metrics: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None


class AlertExplanationResponse(BaseModel):
    explanation: str
    alert_id: str


class RootCauseAnalysisRequest(BaseModel):
    alert: AlertBase
    related_metrics: Optional[Dict[str, Any]] = None
    recent_logs: Optional[List[str]] = None
    topology_info: Optional[Dict[str, Any]] = None


class RootCauseAnalysisResponse(BaseModel):
    analysis: str
    alert_id: str