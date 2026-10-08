"""
Pydantic schemas for metrics data
"""

from pydantic import BaseModel, Field
from typing import List, Union, Optional
import numpy as np


class AnomalyDetectionRequest(BaseModel):
    # Expecting a list of lists or a 2D array
    data: List[List[float]] = Field(..., example=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    # Optional: feature names
    feature_names: Optional[List[str]] = None


class AnomalyDetectionResponse(BaseModel):
    predictions: List[int]  # -1 for anomaly, 1 for normal
    scores: List[float]     # anomaly scores
    anomaly_count: int


class PredictiveMonitoringRequest(BaseModel):
    data: List[float] = Field(..., example=[1.0, 1.2, 1.1, 1.3, 1.5])
    steps: int = Field(1, example=5, ge=1, le=100)


class PredictiveMonitoringResponse(BaseModel):
    predictions: List[float]
    steps: int


class CapacityForecastingRequest(BaseModel):
    data: List[float] = Field(..., example=[50.0, 55.0, 60.0, 65.0, 70.0])
    steps: int = Field(1, example=5, ge=1, le=100)


class CapacityForecastingResponse(BaseModel):
    predictions: List[float]
    steps: int