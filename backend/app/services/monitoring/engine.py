"""Monitoring engine: dispatches probes, evaluates status, records checks,
and raises/resolves incidents.

Engine is decoupled from probe implementations (DIP) and from persistence
details through a repository interface. State transitions are idempotent.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.db.models.monitor import Monitor, MonitorStatus, Check, Incident, IncidentSeverity
from app.services.monitoring.probes import ProbeRegistry, ProbeResult

logger = logging.getLogger(__name__)

# Default failure threshold before marking DOWN
DOWN_THRESHOLD = 3


class MonitoringEngine:
    """Core engine that executes checks and tracks monitor health."""

    def __init__(self, probe_registry: ProbeRegistry):
        self.probes = probe_registry
        self._consecutive_failures: dict = {}  # monitor_id -> count (in-memory)

    def _get_probe(self, monitor_type: str):
        probe = self.probes.get(monitor_type)
        if probe is None:
            raise ValueError(f"No probe registered for type: {monitor_type}")
        return probe

    async def run_check(self, monitor: Monitor) -> ProbeResult:
        """Run a single check for a monitor and update its status.

        This method is pure with respect to side-effect ordering: it computes
        the result, evaluates the new status, and returns both. Persistence is
        handled by the caller (repository) to keep the engine testable.
        """
        if not monitor.is_active or monitor.status == MonitorStatus.PAUSED:
            return ProbeResult(success=True, error_message="Monitor paused/skipped")

        probe = self._get_probe(monitor.type.value)
        result = await probe.execute(monitor, monitor.timeout)

        new_status = self._evaluate_status(monitor, result)
        monitor.status = new_status
        monitor.last_checked_at = datetime.utcnow()
        monitor.response_time_ms = result.response_time_ms
        if result.success:
            monitor.last_status_change = datetime.utcnow()

        # Update availability (rolling approximation)
        self._update_availability(monitor, result)

        return result

    def _evaluate_status(self, monitor: Monitor, result: ProbeResult) -> MonitorStatus:
        """Determine monitor status based on probe result + consecutive failures."""
        key = str(monitor.id)
        if result.success:
            self._consecutive_failures[key] = 0
            return MonitorStatus.UP
        else:
            self._consecutive_failures[key] = self._consecutive_failures.get(key, 0) + 1
            if self._consecutive_failures[key] >= DOWN_THRESHOLD:
                return MonitorStatus.DOWN
            return MonitorStatus.DEGRADED

    def _update_availability(self, monitor: Monitor, result: ProbeResult) -> None:
        """Update rolling availability percentage (simple exponential blend)."""
        current = monitor.availability_percentage or 100.0
        new_point = 100.0 if result.success else 0.0
        # Blend with existing value (weight existing heavily)
        monitor.availability_percentage = round(current * 0.99 + new_point * 0.01, 4)

    def should_raise_incident(self, monitor: Monitor) -> Optional[Incident]:
        """Return a new Incident if a monitor transitions to DOWN, else None."""
        if monitor.status == MonitorStatus.DOWN:
            return Incident(
                tenant_id=monitor.tenant_id,
                monitor_id=monitor.id,
                title=f"Monitor '{monitor.name}' is DOWN",
                description=f"Monitor at {monitor.target} failed consecutive checks.",
                severity=IncidentSeverity.CRITICAL,
                started_at=datetime.utcnow()
            )
        return None

    def should_resolve_incident(self, monitor: Monitor, active_incident: Optional[Incident]) -> bool:
        """Return True if an active incident should be resolved (monitor is UP)."""
        if monitor.status == MonitorStatus.UP and active_incident and not active_incident.is_resolved:
            active_incident.is_resolved = True
            active_incident.resolved_at = datetime.utcnow()
            active_incident.duration_seconds = int(
                (active_incident.resolved_at - active_incident.started_at).total_seconds()
            )
            return True
        return False


class EngineScheduler:
    """Async scheduler that runs checks for monitors at their configured intervals."""

    def __init__(self, engine: MonitoringEngine):
        self.engine = engine
        self._tasks: dict = {}
        self._running = False

    async def start(self, db, monitors):
        """Begin scheduling checks for the provided monitors."""
        self._running = True
        for monitor in monitors:
            task = asyncio.create_task(self._loop(db, monitor))
            self._tasks[str(monitor.id)] = task
        logger.info(f"Scheduler started for {len(monitors)} monitors")

    async def stop(self):
        self._running = False
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()

    async def _loop(self, db, monitor):
        while self._running:
            try:
                # Re-fetch monitor to get latest state
                fresh = await db.get(Monitor, monitor.id)
                if fresh and fresh.is_active:
                    result = await self.engine.run_check(fresh)
                    await self._persist(db, fresh, result)
            except Exception as e:
                logger.error(f"Check loop error for monitor {monitor.id}: {e}")
            await asyncio.sleep(monitor.interval)

    async def _persist(self, db, monitor, result: ProbeResult):
        check = Check(
            monitor_id=monitor.id,
            is_success=result.success,
            response_time_ms=result.response_time_ms,
            status_code=result.status_code,
            error_message=result.error_message,
            metrics_data=result.metrics
        )
        db.add(check)

        incident = self.engine.should_raise_incident(monitor)
        if incident:
            db.add(incident)

        await db.commit()