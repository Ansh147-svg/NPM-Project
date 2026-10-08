"""Monitoring resources models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class MonitorType(str, enum.Enum):
    PING = "ping"
    HTTP = "http"
    TCP = "tcp"
    SNMP = "snmp"
    DNS = "dns"
    SSL = "ssl"


class MonitorStatus(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    PAUSED = "paused"
    PENDING = "pending"


class IncidentSeverity(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class MonitorGroup(Base):
    """Grouping for monitors."""
    __tablename__ = "monitor_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="monitor_groups")
    monitors = relationship("Monitor", back_populates="group", cascade="all, delete-orphan")


class Monitor(Base):
    """Network monitor entity."""
    __tablename__ = "monitors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("monitor_groups.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(MonitorType), nullable=False)
    target = Column(String(500), nullable=False)  # IP, URL, Hostname, etc.
    port = Column(Integer, nullable=True)
    interval = Column(Integer, default=60)  # Check interval in seconds
    timeout = Column(Integer, default=10)   # Timeout in seconds
    
    status = Column(SQLEnum(MonitorStatus), default=MonitorStatus.PENDING, index=True)
    is_active = Column(Boolean, default=True)
    
    config = Column(JSON, default=dict)  # Type-specific configuration (headers, SNMP OIDs, etc.)
    tags = Column(JSON, default=list)
    
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_status_change = Column(DateTime(timezone=True), nullable=True)
    response_time_ms = Column(Float, nullable=True)
    availability_percentage = Column(Float, default=100.0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="monitors")
    group = relationship("MonitorGroup", back_populates="monitors")
    agent = relationship("Agent", back_populates="monitors")
    checks = relationship("Check", back_populates="monitor", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="monitor", cascade="all, delete-orphan")


class Check(Base):
    """Individual monitor check result history."""
    __tablename__ = "checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitor_id = Column(UUID(as_uuid=True), ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    is_success = Column(Boolean, nullable=False)
    response_time_ms = Column(Float, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    metrics_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    monitor = relationship("Monitor", back_populates="checks")


class Incident(Base):
    """Monitor outages and performance incidents."""
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitor_id = Column(UUID(as_uuid=True), ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(SQLEnum(IncidentSeverity), default=IncidentSeverity.CRITICAL)
    
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    is_resolved = Column(Boolean, default=False, index=True)
    
    # Relationships
    monitor = relationship("Monitor", back_populates="incidents")
    tenant = relationship("Tenant", backref="incidents")


class NotificationChannel(Base):
    """Notification endpoints (Email, Slack, Webhook, PagerDuty)."""
    __tablename__ = "notification_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # email, slack, webhook, telegram
    config = Column(JSON, nullable=False)      # endpoint URL, auth tokens, channel name
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="notification_channels")
    user = relationship("User", back_populates="notification_channels")


class AlertRule(Base):
    """Alerting rules linked to monitors and notification channels."""
    __tablename__ = "alert_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    monitor_id = Column(UUID(as_uuid=True), ForeignKey("monitors.id", ondelete="CASCADE"), nullable=True)
    
    name = Column(String(255), nullable=False)
    condition = Column(JSON, nullable=False)    # e.g., {"metric": "response_time", "operator": ">", "threshold": 500}
    for_duration = Column(Integer, default=0)   # duration in seconds before triggering
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="alert_rules")
    monitor = relationship("Monitor", backref="alert_rules")