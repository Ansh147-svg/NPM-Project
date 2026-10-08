"""Tests for database models."""
import pytest
from datetime import datetime
from app.db.models.user import User, Role, Permission
from app.db.models.tenant import Tenant
from app.db.models.monitor import Monitor, MonitorType, MonitorStatus
from app.db.models.agent import Agent
from app.db.models.audit import AuditLog
import uuid


def test_user_creation():
    """User model creates with required fields."""
    tenant = Tenant(name="Test Tenant", slug="test-tenant")
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        tenant=tenant
    )
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_role_creation():
    """Role model creates with required fields."""
    role = Role(name="admin", description="Administrator role")
    assert role.name == "admin"


def test_permission_creation():
    """Permission model creates with required fields."""
    perm = Permission(name="monitors.create", resource="monitors", action="create")
    assert perm.resource == "monitors"
    assert perm.action == "create"


def test_monitor_creation():
    """Monitor model creates with required fields."""
    monitor = Monitor(
        tenant_id=uuid.uuid4(),
        name="Test Monitor",
        type=MonitorType.PING,
        target="192.168.1.1"
    )
    assert monitor.target == "192.168.1.1"
    assert monitor.status == MonitorStatus.PENDING


def test_agent_creation():
    """Agent model creates with required fields."""
    agent = Agent(
        tenant_id=uuid.uuid4(),
        name="Agent-1",
        version="1.0.0",
        hostname="host1",
        ip_address="192.168.1.1",
        api_key_hash="hashed-key"
    )
    assert agent.hostname == "host1"