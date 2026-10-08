"""Metrics ingestion and query endpoints (InfluxDB-backed)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
from app.services.metrics_service import MetricsService
from app.core.dependencies import get_metrics_service

router = APIRouter()


class MetricPoint(BaseModel):
    measurement: str
    fields: Dict[str, float]
    tags: Dict[str, str] = {}
    timestamp: str  # RFC3339


class IngestRequest(BaseModel):
    points: List[MetricPoint]


class QueryRequest(BaseModel):
    monitor_id: uuid.UUID
    metric: str = "response_time"
    start_time: str
    end_time: str
    aggregate: str = "mean"  # mean, max, min, count
    interval: str = "1m"


class QueryResponse(BaseModel):
    monitor_id: str
    metric: str
    points: List[Dict[str, Any]]


@router.post("/ingest", status_code=202)
async def ingest_metrics(
    request: IngestRequest,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Bulk ingest metrics into InfluxDB."""
    await metrics_service.write_points(
        measurement=request.points[0].measurement if request.points else "metrics",
        points=[p.model_dump() for p in request.points]
    )
    return {"status": "accepted", "count": len(request.points)}


@router.get("/query", response_model=QueryResponse)
async def query_metrics(
    monitor_id: uuid.UUID,
    metric: str = "response_time",
    start_time: str = "now()-1h",
    end_time: str = "now()",
    aggregate: str = "mean",
    interval: str = "1m",
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Query historical metrics from InfluxDB."""
    points = await metrics_service.query_range(
        monitor_id=monitor_id,
        metric=metric,
        start_time=start_time,
        end_time=end_time,
        aggregate=aggregate,
        interval=interval
    )
    return QueryResponse(
        monitor_id=str(monitor_id),
        metric=metric,
        points=points
    )