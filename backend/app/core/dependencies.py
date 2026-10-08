"""Dependency injection container for services."""
from app.services.metrics_service import MetricsService

# Singleton instances for FastAPI dependency injection
_metrics_service: MetricsService = None


def get_metrics_service() -> MetricsService:
    """Get or create metrics service singleton."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service