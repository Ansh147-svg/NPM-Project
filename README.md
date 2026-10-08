# Network Monitoring Platform

A production-grade network monitoring solution built with Next.js, FastAPI, PostgreSQL, InfluxDB, and Redis. Inspired by NetCrunch, PRTG, and Zabbix.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js Frontend  │◄──►│   FastAPI Backend  │◄──►│   Agents (Python) │
│  (TypeScript/Tailwind) │  (Python/SQLAlchemy) │  (Monitoring)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL     │    │   Redis (Cache)   │    │   InfluxDB       │
│   (Primary DB)   │    │   (Sessions/Queue) │    │   (Metrics)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, TailwindCSS, React Query
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy, Pydantic
- **Database**: PostgreSQL 15+
- **Metrics**: InfluxDB 2.x
- **Cache**: Redis 7+
- **Auth**: JWT + RBAC
- **Deployment**: Docker + Docker Compose
- **Testing**: pytest, Jest

## Features

- ✅ Multi-tenant monitoring
- ✅ Role-Based Access Control (RBAC)
- ✅ Real-time metrics collection
- ✅ Alerting & notifications
- ✅ Dashboard & visualization
- ✅ Agent-based monitoring
- ✅ SNMP, ICMP, HTTP, TCP probes
- ✅ REST API with OpenAPI/Swagger
- ✅ Docker containerization

## Quick Start

From PowerShell, run these commands from the repository root. Docker Desktop
must be running:

```powershell
docker compose up -d --build
docker compose ps
```

Open the frontend at http://localhost:3000 and the API docs at
http://localhost:8000/docs. To view service logs, run
`docker compose logs -f backend` (replace `backend` with another service name
as needed). Stop the services with `docker compose down`.

### Create an account and sign in

1. Open http://localhost:3000/signup.
2. Enter your email, a password, your full name, an organization name, and a
   unique organization slug (for example, `acme-network-team`).
3. Select **Create Account**. After the account is created, the app opens the
   sign-in page.
4. Sign in using the same email and password, then select **Sign in**. You
   should arrive at the dashboard.

Each email address and organization slug must be unique. If account creation
fails because either is already registered, choose a different one.

### Add a monitoring agent on Windows

1. Start the platform and create/sign in to your account using the steps above.
   Keep the backend running at http://localhost:8000.
2. Open http://localhost:8000/docs and select **Authorize**. Sign in with the
   same account email and password.
3. Expand `POST /api/v1/agents/register`, select **Try it out**, and submit
   agent details. For example:

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

   Use your Windows computer's hostname and IPv4 address. You can get them in
   PowerShell with:

   ```powershell
   $env:COMPUTERNAME
   Get-NetIPConfiguration | Where-Object IPv4DefaultGateway |
     ForEach-Object { $_.IPv4Address.IPAddress }
   ```

   Copy the returned `id` and `api_key` and keep the API key private; it is
   only returned during registration.
4. On the Windows machine, open PowerShell and install the agent dependencies:

   ```powershell
   cd C:\NPM-Project\agent
   py -3.11 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   If you are installing the agent on a different Windows computer, first copy
   the `agent` folder there and change to that folder.
5. Set the connection details using the values returned in step 3, then start
   the agent:

   ```powershell
   $env:BACKEND_URL = "http://localhost:8000"
   $env:AGENT_ID = "<agent-id-from-registration>"
   $env:AGENT_API_KEY = "<api-key-from-registration>"
   .\.venv\Scripts\python.exe .\agent.py
   ```

   For an agent on another computer, replace `localhost` with the backend
   computer's reachable IP or DNS name, for example
   `http://192.168.1.20:8000`. Allow inbound TCP port 8000 through the backend
   computer's firewall and ensure both machines can reach each other.
6. Keep the PowerShell window open. The agent sends a heartbeat every 15
   seconds. Refresh http://localhost:3000/agents to see its status.

The current agent reports its heartbeat/status; it does not yet run monitor
checks on the Windows host.

## Documentation

- [API Documentation](./docs/API.md)
- [Database Schema](./docs/DATABASE_SCHEMA.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Kubernetes Deployment](./k8s/README.md)

## Kubernetes Deployment

The Kubernetes manifests are packaged as a Helm chart in `k8s/`. Use
`helm upgrade --install` so the same command installs a release the first time
and upgrades it on later runs. Run these commands from the repository root:

```powershell
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add influxdata https://helm.influxdata.com
helm repo update

helm upgrade --install postgres bitnami/postgresql `
  --set auth.username=user `
  --set auth.password="REPLACE_WITH_DATABASE_PASSWORD" `
  --set auth.database=monitoring

helm upgrade --install influxdb influxdata/influxdb `
  --set influxdb.username=admin `
  --set influxdb.password="REPLACE_WITH_INFLUXDB_PASSWORD" `
  --set influxdb.database=monitoring

helm upgrade --install netvision ./k8s `
  -f k8s/production/values.yaml
```

Use `k8s/staging/values.yaml` instead for staging. Helm release names are
scoped to a namespace: if an existing release is in a non-default namespace,
pass the same `--namespace <namespace>` to its `helm upgrade --install`
command. Replace placeholder credentials and secret values before deploying.

## License

Proprietary