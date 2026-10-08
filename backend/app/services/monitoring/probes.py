"""Monitoring engine: probe implementations using Strategy pattern.

Each probe type (ICMP, HTTP, TCP) implements a common interface,
satisfying the Open/Closed Principle — new probe types can be added
without modifying existing code or the engine that dispatches them.
"""
import abc
import asyncio
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from app.db.models.monitor import Monitor


@dataclass
class ProbeResult:
    """Immutable result of a single probe execution."""
    success: bool
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)


class BaseProbe(abc.ABC):
    """Abstract probe strategy. All concrete probes implement execute()."""

    @property
    @abc.abstractmethod
    def probe_type(self) -> str:
        """Return the monitor type this probe handles."""
        ...

    @abc.abstractmethod
    async def execute(self, monitor: Monitor, timeout: int) -> ProbeResult:
        """Execute a probe against the monitor target."""
        ...


class ICMPProbe(BaseProbe):
    """Ping probe using asyncio subprocess (cross-platform where possible)."""

    @property
    def probe_type(self) -> str:
        return "ping"

    async def execute(self, monitor: Monitor, timeout: int) -> ProbeResult:
        start = time.perf_counter()
        try:
            # Use platform-appropriate ping command
            import sys
            if sys.platform == "win32":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), monitor.target]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), monitor.target]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout + 2)
            elapsed = (time.perf_counter() - start) * 1000
            
            if process.returncode == 0:
                # Parse RTT from output (best effort)
                rtt = self._parse_rtt(stdout.decode(errors="ignore"))
                return ProbeResult(
                    success=True,
                    response_time_ms=elapsed,
                    metrics={"rtt_ms": rtt or elapsed}
                )
            return ProbeResult(success=False, response_time_ms=elapsed, error_message="Ping failed")
        except asyncio.TimeoutError:
            return ProbeResult(success=False, error_message="Ping timeout")
        except Exception as e:
            return ProbeResult(success=False, error_message=str(e))

    @staticmethod
    def _parse_rtt(output: str) -> Optional[float]:
        """Extract round-trip time from ping output (best effort)."""
        try:
            for line in output.splitlines():
                if "time" in line or "time=" in line:
                    parts = line.split("time=")[-1].split(" ms")[0]
                    return float(parts)
        except (ValueError, IndexError):
            pass
        return None


class HTTPProbe(BaseProbe):
    """HTTP(S) status and latency probe."""

    @property
    def probe_type(self) -> str:
        return "http"

    async def execute(self, monitor: Monitor, timeout: int) -> ProbeResult:
        import aiohttp
        start = time.perf_counter()
        url = monitor.target
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        if monitor.port and ":" not in url.split("/")[2]:
            url = url.replace(f":{monitor.port}", "")  # avoid double-port
            host = url.split("/")[2]
            url = url.replace(host, f"{host}:{monitor.port}")

        config = monitor.config or {}
        headers = config.get("headers", {})
        method = config.get("method", "GET").upper()
        expected_status = config.get("expected_status", 200)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    body = await resp.read()
                    elapsed = (time.perf_counter() - start) * 1000
                    success = resp.status == expected_status
                    return ProbeResult(
                        success=success,
                        response_time_ms=elapsed,
                        status_code=resp.status,
                        error_message=None if success else f"Expected {expected_status}, got {resp.status}",
                        metrics={
                            "response_time_ms": elapsed,
                            "content_length": float(len(body)),
                            "status_code": float(resp.status)
                        }
                    )
        except Exception as e:
            return ProbeResult(success=False, error_message=str(e))


class TCPProbe(BaseProbe):
    """TCP port reachability probe."""

    @property
    def probe_type(self) -> str:
        return "tcp"

    async def execute(self, monitor: Monitor, timeout: int) -> ProbeResult:
        start = time.perf_counter()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(monitor.target, monitor.port or 80),
                timeout=timeout
            )
            elapsed = (time.perf_counter() - start) * 1000
            writer.close()
            await writer.wait_closed()
            return ProbeResult(
                success=True,
                response_time_ms=elapsed,
                metrics={"tcp_connect_ms": elapsed}
            )
        except asyncio.TimeoutError:
            return ProbeResult(success=False, error_message="TCP connection timeout")
        except ConnectionRefusedError:
            return ProbeResult(success=False, error_message="Connection refused")
        except Exception as e:
            return ProbeResult(success=False, error_message=str(e))


class ProbeRegistry:
    """Registry mapping monitor types to probe strategies (Strategy + Registry pattern)."""

    def __init__(self):
        self._probes: Dict[str, BaseProbe] = {}
        for probe in (ICMPProbe(), HTTPProbe(), TCPProbe()):
            self.register(probe)

    def register(self, probe: BaseProbe) -> None:
        self._probes[probe.probe_type] = probe

    def get(self, monitor_type: str) -> Optional[BaseProbe]:
        return self._probes.get(monitor_type)