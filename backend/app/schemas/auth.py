"""Authentication schemas."""
from pydantic import BaseModel
from typing import Optional
import uuid


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    type: str = "access"
    tenant_id: Optional[uuid.UUID] = None