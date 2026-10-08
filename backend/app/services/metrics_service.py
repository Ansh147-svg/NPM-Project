"""Metrics service for InfluxDB operations."""
from typing import List, Dict, Any
import uuid
from influxdb_client import InfluxDBClient
from app.config import settings


class MetricsService:
    """Service interface for metrics storage and retrieval."""
    
    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options="synchronous")
        self.query_api = self.client.query_api()
    
    async def write_points(
        self,
        measurement: str,
        points: List[Dict[str, Any]]
    ) -> None:
        """Write metric points to InfluxDB."""
        for point in points:
            self.write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                record={
                    "measurement": measurement,
                    "fields": point.get("fields", {}),
                    "tags": point.get("tags", {}),
                    "time": point.get("timestamp")
                }
            )
    
    async def query_range(
        self,
        monitor_id: uuid.UUID,
        metric: str,
        start_time: str,
        end_time: str,
        aggregate: str = "mean",
        interval: str = "1m"
    ) -> List[Dict[str, Any]]:
        """Query metric range with aggregation."""
        query = f'''
            FROM(bucket:"{settings.INFLUXDB_BUCKET}")
            |> range(start: {start_time}, stop: {end_time})
            |> filter(fn: (r) => r._measurement == "metrics" and r.monitor_id == "{monitor_id}")
            |> filter(fn: (r) => r._field == "{metric}")
            |> aggregateWindow(every: {interval}, fn: {aggregate})
            |> yield(name: "table")
        '''
        tables = self.query_api.query_tables(query)
        return [
            {"time": str(table.time), "value": table.get_value()}
            for table in tables
        ]
    
    def close(self):
        self.client.close()