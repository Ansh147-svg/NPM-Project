"""User and RBAC models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


# Many-to-many relationship tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(Base):
    """System permissions for RBAC."""
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    resource = Column(String(50), nullable=False)  # e.g., "monitors", "users"
    action = Column(String(50), nullable=False)    # e.g., "create", "read", "update", "delete"
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Permission(name={self.name})>"


class Role(Base):
    """User roles with associated permissions."""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(500))
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, backref="roles")
    users = relationship("User", secondary=user_roles, backref="roles")
    
    def __repr__(self):
        return f"<Role(name={self.name})>"


class User(Base):
    """System user with authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    notification_channels = relationship("NotificationChannel", back_populates="user")
    
    def __repr__(self):
        return f"<User(email={self.email})>"