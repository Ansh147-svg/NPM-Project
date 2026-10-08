"""Agent management and heartbeat endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.db.models.agent import Agent
from app.db.models.user import User
from app.api.dependencies import get_current_user
from app.core.security import get_password_hash, verify_password

router = APIRouter()


class AgentRegister(BaseModel):
    name: str
    version: str
    hostname: str
    ip_address: str
    system_info: dict = Field(default_factory=dict)


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    hostname: str
    ip_address: str
    is_active: bool
    is_online: bool
    last_heartbeat: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgentRegisteredResponse(AgentResponse):
    api_key: str


@router.post("/register", response_model=AgentRegisteredResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    agent_in: AgentRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a new monitoring agent."""
    if not current_user.tenant_id:
        raise HTTPException(status_code=400, detail="User is not associated with a tenant")

    # Generate a secure API key for agent authentication
    api_key = uuid.uuid4().hex + uuid.uuid4().hex
    api_key_hash = get_password_hash(api_key)
    
    agent = Agent(
        tenant_id=current_user.tenant_id,
        name=agent_in.name,
        version=agent_in.version,
        hostname=agent_in.hostname,
        ip_address=agent_in.ip_address,
        api_key_hash=api_key_hash,
        system_info=agent_in.system_info
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Return plaintext API key only once
    return AgentRegisteredResponse.model_validate({
        **AgentResponse.model_validate(agent).model_dump(),
        "api_key": api_key,
    })


@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Header(alias="X-Agent-API-Key"),
):
    """Agent heartbeat to maintain online status."""
    agent = await db.get(Agent, agent_id)
    if (
        not agent
        or not agent.is_active
        or len(api_key) != 64
        or not verify_password(api_key, agent.api_key_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid agent credentials")
        
    agent.is_online = True
    agent.last_heartbeat = datetime.utcnow()
    await db.commit()
    return {"status": "ok"}


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all agents for a tenant."""
    query = select(Agent).where(Agent.tenant_id == current_user.tenant_id)
    result = await db.execute(query)
    return result.scalars().all()