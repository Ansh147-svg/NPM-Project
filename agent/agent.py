"""Distributed Monitoring Agent.

Pulls target monitor configs from the central server, runs ICMP/HTTP/TCP probes
locally using a modular execution strategy, and pushes results back to the metrics server.
"""
import asyncio
import logging
import time
import sys
import os
import uuid
import aiohttp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MonitoringAgent")


class MonitoringAgent:
    """Agent running on a distributed host to perform remote probes."""

    def __init__(self, backend_url: str, api_key: str, agent_id: str, check_interval: int = 15):
        self.backend_url = backend_url
        self.api_key = api_key
        self.agent_id = agent_id
        self.check_interval = check_interval
        self.headers = {"X-Agent-API-Key": self.api_key}
        self.running = False

    async def register(self) -> bool:
        """Register agent with back-end API."""
        url = f"{self.backend_url}/api/v1/agents/register"
        payload = {
            "name": f"Agent-{os.uname().nodename if hasattr(os, 'uname') else 'Windows'}",
            "version": "1.0.0",
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "Windows",
            "ip_address": "127.0.0.1",
            "system_info": {"platform": sys.platform}
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 201:
                        logger.info("Agent registered successfully.")
                        return True
                    else:
                        logger.error(f"Failed to register agent. Code: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False

    async def heartbeat(self) -> None:
        """Maintain online status via heartbeat."""
        url = f"{self.backend_url}/api/v1/agents/{self.agent_id}/heartbeat"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, timeout=5) as resp:
                    if resp.status == 200:
                        logger.debug("Heartbeat succeeded")
                    else:
                        logger.error(f"Heartbeat failed with status: {resp.status}")
        except Exception as e:
            logger.error(f"Heartbeat exception: {e}")

    async def run(self) -> None:
        """Main agent scheduling loop."""
        self.running = True
        logger.info(f"Starting Monitoring Agent {self.agent_id}...")
        while self.running:
            start_time = time.time()
            await self.heartbeat()
            # Agent can query backend for assigned monitors, execute probes, and post back
            elapsed = time.time() - start_time
            sleep_time = max(0, self.check_interval - elapsed)
            await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    backend_url = os.getenv("BACKEND_URL")
    api_key = os.getenv("AGENT_API_KEY")
    agent_id = os.getenv("AGENT_ID")

    missing = [
        name for name, value in (
            ("BACKEND_URL", backend_url),
            ("AGENT_API_KEY", api_key),
            ("AGENT_ID", agent_id),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

    try:
        uuid.UUID(agent_id)
    except ValueError as exc:
        raise SystemExit("AGENT_ID must be the UUID returned by agent registration") from exc
    
    agent = MonitoringAgent(backend_url, api_key, agent_id)
    asyncio.run(agent.run())