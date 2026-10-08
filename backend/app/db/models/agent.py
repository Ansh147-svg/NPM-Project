"""Monitoring agent model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Agent(Base):
    """Distributed monitoring agent."""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    
    api_key_hash = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False, index=True)
    
    system_info = Column(JSON, default=dict)  # OS, CPU, Memory specs
    
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="agents")
    monitors = relationship("Monitor", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(name={self.name}, hostname={self.hostname})>"