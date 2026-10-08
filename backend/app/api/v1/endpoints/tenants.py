"""Tenant management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.tenant import Tenant

router = APIRouter()


class TenantCreate(BaseModel):
    name: str
    slug: str
    description: str = ""
    max_monitors: int = 100


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str
    is_active: bool
    max_monitors: int

    model_config = {"from_attributes": True}


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tenant."""
    query = select(Tenant).where(Tenant.slug == tenant_in.slug)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Slug already exists")
        
    tenant = Tenant(
        name=tenant_in.name,
        slug=tenant_in.slug,
        description=tenant_in.description,
        max_monitors=tenant_in.max_monitors
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all tenants."""
    query = select(Tenant).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get tenant by ID."""
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant