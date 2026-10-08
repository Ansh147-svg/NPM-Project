"""API V1 Router configuration."""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, monitors, metrics, agents, tenants, ai_operations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(monitors.router, prefix="/monitors", tags=["Monitors"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(ai_operations.router, prefix="/ai-operations", tags=["AI Operations"])