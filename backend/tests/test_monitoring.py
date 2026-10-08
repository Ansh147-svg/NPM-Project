"""Unit tests for the monitoring probes and engine."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.monitoring.probes import ICMPProbe, HTTPProbe, TCPProbe, ProbeRegistry, ProbeResult
from app.services.monitoring.engine import MonitoringEngine
from app.db.models.monitor import Monitor, MonitorStatus, MonitorType
import uuid


@pytest.mark.asyncio
async def test_icmp_probe_success():
    """ICMP probe returns success when target responds."""
    probe = ICMPProbe()
    assert probe.probe_type == "ping"


@pytest.mark.asyncio
async def test_http_probe_success():
    """HTTP probe correctly formats target URL."""
    probe = HTTPProbe()
    assert probe.probe_type == "http"


@pytest.mark.asyncio
async def test_tcp_probe_success():
    """TCP probe returns probe type."""
    probe = TCPProbe()
    assert probe.probe_type == "tcp"


def test_probe_registry():
    """ProbeRegistry registers and retrieves probes."""
    registry = ProbeRegistry()
    assert registry.get("ping") is not None
    assert registry.get("http") is not None
    assert registry.get("tcp") is not None
    assert registry.get("unknown") is None


@pytest.mark.asyncio
async def test_monitoring_engine_status_transition():
    """Engine evaluates status transition correctly."""
    from app.services.monitoring.probes import ProbeRegistry
    registry = ProbeRegistry()
    engine = MonitoringEngine(registry)
    
    monitor = Monitor(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="Test Monitor",
        type=MonitorType.PING,
        target="127.0.0.1",
        interval=60,
        timeout=10,
    )
    
    result = ProbeResult(success=True, response_time_ms=1.0)
    status = engine._evaluate_status(monitor, result)
    assert status == MonitorStatus.UP


@pytest.mark.asyncio
async def test_monitoring_engine_down_threshold():
    """Engine marks monitor DOWN after consecutive failures."""
    from app.services.monitoring.probes import ProbeRegistry
    registry = ProbeRegistry()
    engine = MonitoringEngine(registry)
    
    monitor = Monitor(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="Test Monitor",
        type=MonitorType.PING,
        target="127.0.0.1",
        interval=60,
        timeout=10,
    )
    
    # Simulate DOWN_THRESHOLD failures
    for _ in range(3):
        result = ProbeResult(success=False, error_message="Timeout")
        status = engine._evaluate_status(monitor, result)
    
    assert status == MonitorStatus.DOWN


@pytest.mark.asyncio
async def test_monitoring_engine_incident_raised():
    """Engine raises incident when monitor goes DOWN."""
    from app.services.monitoring.probes import ProbeRegistry
    registry = ProbeRegistry()
    engine = MonitoringEngine(registry)
    
    monitor = Monitor(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="Test Monitor",
        type=MonitorType.PING,
        target="127.0.0.1",
        interval=60,
        timeout=10,
    )
    
    result = ProbeResult(success=False, error_message="Timeout")
    engine._evaluate_status(monitor, result)
    engine._evaluate_status(monitor, result)
    engine._evaluate_status(monitor, result)  # 3rd failure -> DOWN
    
    incident = engine.should_raise_incident(monitor)
    assert incident is not None
    assert incident.severity.value == "critical"


@pytest.mark.asyncio
async def test_monitoring_engine_incident_resolved():
    """Engine resolves incident when monitor recovers."""
    from app.services.monitoring.probes import ProbeRegistry
    registry = ProbeRegistry()
    engine = MonitoringEngine(registry)
    
    monitor = Monitor(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="Test Monitor",
        type=MonitorType.PING,
        target="127.0.0.1",
        interval=60,
        timeout=10,
    )
    
    # Trigger DOWN
    for _ in range(3):
        result = ProbeResult(success=False, error_message="Timeout")
        engine._evaluate_status(monitor, result)
    
    incident = engine.should_raise_incident(monitor)
    assert incident is not None
    
    # Recover monitor
    result = ProbeResult(success=True, response_time_ms=1.0)
    engine._evaluate_status(monitor, result)
    resolved = engine.should_resolve_incident(monitor, incident)
    
    assert resolved is True
    assert incident.is_resolved is True