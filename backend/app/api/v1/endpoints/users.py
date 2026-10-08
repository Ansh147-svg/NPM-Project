"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid
from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_password_hash
from pydantic import BaseModel, EmailStr

router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    tenant_id: uuid.UUID


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    tenant_id: uuid.UUID

    model_config = {"from_attributes": True}


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        tenant_id=user_in.tenant_id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all users."""
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()