# API Documentation

## Base URL

`http://localhost:8000/api/v1`

## Authentication

All endpoints (except `/auth/login` and `/health`) require a Bearer token.

```
Authorization: Bearer <access_token>
```

### Get Token

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

email=test@example.com&password=secret
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_superuser": false,
    "tenant_id": "uuid"
  }
}
```

## Endpoints

### Monitors

| Method | Path | Description |
|--------|------|-------------|
| GET | `/monitors/` | List monitors (query: `tenant_id`, `status`) |
| POST | `/monitors/` | Create monitor |
| GET | `/monitors/{id}` | Get monitor |
| PUT | `/monitors/{id}` | Update monitor |
| DELETE | `/monitors/{id}` | Delete monitor |
| GET | `/monitors/{id}/checks` | Monitor check history |
| GET | `/monitors/{id}/incidents` | Monitor incident history |

### Metrics

| Method | Path | Description |
|--------|------|-------------|
| POST | `/metrics/ingest` | Bulk ingest metrics |
| GET | `/metrics/query` | Query metrics (params: `monitor_id`, `metric`, `start_time`, `end_time`) |

### Agents

| Method | Path | Description |
|--------|------|-------------|
| POST | `/agents/register` | Register agent for the authenticated user's tenant; returns its API key once |
| POST | `/agents/{id}/heartbeat` | Agent heartbeat (requires `X-Agent-API-Key`) |
| GET | `/agents/` | List agents for the authenticated user's tenant |

Register an agent with the access token from `/auth/login` and a JSON body:

```json
{
  "name": "Windows monitoring agent",
  "version": "1.0.0",
  "hostname": "YOUR-WINDOWS-PC",
  "ip_address": "192.168.1.50",
  "system_info": {
    "platform": "Windows"
  }
}
```

The registration response includes `id` and `api_key`. Configure both on the
agent host; the key is hashed by the API and cannot be retrieved later.

### Users & Tenants

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/` | Create user |
| GET | `/users/` | List users |
| POST | `/tenants/` | Create tenant |
| GET | `/tenants/` | List tenants |

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |