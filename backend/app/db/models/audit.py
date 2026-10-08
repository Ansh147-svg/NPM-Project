"""Audit log model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class AuditLog(Base):
    """Security and administrative audit trail."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)  # e.g., "user.login", "monitor.create"
    resource_type = Column(String(100), nullable=False)        # e.g., "monitor", "user"
    resource_id = Column(String(100), nullable=True)
    
    ip_address = Column(String(45))
    user_agent = Column(Text)
    details = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    tenant = relationship("Tenant", backref="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, user_id={self.user_id})>"