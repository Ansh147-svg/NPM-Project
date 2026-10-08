"""Monitor management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Any
import uuid
from datetime import datetime
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.monitor import Monitor, MonitorType, MonitorStatus, Check
from app.db.models.monitor import Incident

router = APIRouter()


class MonitorCreate(BaseModel):
    name: str
    type: MonitorType
    target: str
    port: Optional[int] = None
    interval: int = 60
    timeout: int = 10
    group_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    config: dict = {}
    tags: list = []


class MonitorUpdate(BaseModel):
    name: Optional[str] = None
    target: Optional[str] = None
    port: Optional[int] = None
    interval: Optional[int] = None
    timeout: Optional[int] = None
    is_active: Optional[bool] = None
    config: Optional[dict] = None


class MonitorResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: MonitorType
    target: str
    port: Optional[int]
    interval: int
    timeout: int
    status: MonitorStatus
    is_active: bool
    last_checked_at: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    availability_percentage: float

    model_config = {"from_attributes": True}


@router.post("/", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor_in: MonitorCreate,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Create a new monitor."""
    monitor = Monitor(
        tenant_id=tenant_id,
        name=monitor_in.name,
        type=monitor_in.type,
        target=monitor_in.target,
        port=monitor_in.port,
        interval=monitor_in.interval,
        timeout=monitor_in.timeout,
        group_id=monitor_in.group_id,
        agent_id=monitor_in.agent_id,
        config=monitor_in.config,
        tags=monitor_in.tags
    )
    db.add(monitor)
    await db.commit()
    await db.refresh(monitor)
    return monitor


@router.get("/", response_model=List[MonitorResponse])
async def list_monitors(
    tenant_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    status: Optional[MonitorStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List monitors for a tenant with optional filtering."""
    query = select(Monitor).where(Monitor.tenant_id == tenant_id)
    if status:
        query = query.where(Monitor.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(
    monitor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get monitor by ID."""
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(
    monitor_id: uuid.UUID,
    monitor_in: MonitorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a monitor."""
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
        
    for field, value in monitor_in.dict(exclude_unset=True).items():
        setattr(monitor, field, value)
        
    await db.commit()
    await db.refresh(monitor)
    return monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(
    monitor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a monitor."""
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await db.delete(monitor)
    await db.commit()


@router.get("/{monitor_id}/checks", response_model=List[dict])
async def get_monitor_checks(
    monitor_id: uuid.UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get check history for a monitor."""
    query = (
        select(Check)
        .where(Check.monitor_id == monitor_id)
        .order_by(Check.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    checks = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "is_success": c.is_success,
            "response_time_ms": c.response_time_ms,
            "status_code": c.status_code,
            "error_message": c.error_message,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in checks
    ]


@router.get("/{monitor_id}/incidents", response_model=List[dict])
async def get_monitor_incidents(
    monitor_id: uuid.UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get incident history for a monitor."""
    query = (
        select(Incident)
        .where(Incident.monitor_id == monitor_id)
        .order_by(Incident.started_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    incidents = result.scalars().all()
    return [
        {
            "id": str(i.id),
            "title": i.title,
            "severity": i.severity,
            "started_at": i.started_at.isoformat() if i.started_at else None,
            "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
            "is_resolved": i.is_resolved
        }
        for i in incidents
    ]