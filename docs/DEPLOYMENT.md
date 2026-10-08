# Deployment Guide

## Prerequisites

- Docker 24.x or later
- Docker Compose v2
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd network-monitoring-platform

# Copy environment files and customize
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Build and start all services
docker-compose up -d --build

# Check service health
docker-compose ps
```

## Accessing Services

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| Frontend | http://localhost:3000 | - |
| API Docs | http://localhost:8000/docs | - |
| InfluxDB | http://localhost:8086 | admin / admin-pass |

## Production Deployment

### Environment Variables

Set these before production deployment:

```bash
# Backend
SECRET_KEY=<generate-256-bit-secret>
DATABASE_URL=postgresql://user:password@postgres:5432/monitoring
INFLUXDB_TOKEN=<generate-token>

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
```

### SSL/TLS

Use a reverse proxy (nginx, Traefik) in front of the services:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://frontend:3000;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```

### Database Backups

```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U user monitoring > backup.sql

# InfluxDB backup
docker-compose exec influxdb influxd backup /tmp/backup
```

## Monitoring

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Resource usage
docker stats
```