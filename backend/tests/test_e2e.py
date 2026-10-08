"""End-to-end test for monitor creation flow."""
import pytest
from httpx import AsyncClient
from app.main import app
from app.db.models.tenant import Tenant
from app.db.models.user import User
import uuid


@pytest.mark.asyncio
async def test_monitor_creation_flow():
    """Test full flow: create tenant, user, login, create monitor."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create tenant
        tenant_res = await client.post("/api/v1/tenants/", json={
            "name": "Test Tenant",
            "slug": "test-tenant",
            "description": "Test tenant"
        })
        assert tenant_res.status_code == 201
        tenant_data = tenant_res.json()
        tenant_id = tenant_data["id"]
        
        # Create user
        user_res = await client.post("/api/v1/users/", json={
            "email": "test@example.com",
            "password": "secure-password-123",
            "full_name": "Test User",
            "tenant_id": tenant_id
        })
        assert user_res.status_code == 201
        
        # Login
        login_res = await client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "secure-password-123"
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data["access_token"]
        
        # Create monitor
        monitor_res = await client.post("/api/v1/monitors/", json={
            "name": "Test HTTP Monitor",
            "type": "http",
            "target": "http://httpbin.org/get",
            "interval": 30,
            "timeout": 10
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert monitor_res.status_code == 201
        monitor_data = monitor_res.json()
        assert monitor_data["name"] == "Test HTTP Monitor"
        assert monitor_data["type"] == "http"