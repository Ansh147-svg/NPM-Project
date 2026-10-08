const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const api = {
  auth: {
    login: () => `${API_BASE}/auth/login`,
  },
  monitors: {
    list: (tenantId: string) => `${API_BASE}/monitors/?tenant_id=${tenantId}`,
    create: (tenantId: string) => `${API_BASE}/monitors/?tenant_id=${tenantId}`,
  },
  metrics: {
    ingest: () => `${API_BASE}/metrics/ingest`,
    query: (monitorId: string) => `${API_BASE}/metrics/query?monitor_id=${monitorId}`,
  },
}

export default api