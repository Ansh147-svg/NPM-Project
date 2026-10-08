# Database Schema

## PostgreSQL (Primary)

### Tables

#### users
- `id` (UUID, PK) - User ID
- `email` (VARCHAR 255, UNIQUE, INDEX) - Email address
- `hashed_password` (VARCHAR 255) - Bcrypt hash
- `full_name` (VARCHAR 255) - Display name
- `is_active` (BOOL) - Account active flag
- `is_verified` (BOOL) - Email verified
- `is_superuser` (BOOL) - Superuser flag
- `tenant_id` (UUID, FK) - Tenant ownership
- `last_login` (TIMESTAMPTZ) - Last login timestamp
- `created_at` (TIMESTAMPTZ) - Record creation
- `updated_at` (TIMESTAMPTZ) - Last update

#### tenants
- `id` (UUID, PK) - Tenant ID
- `name` (VARCHAR 255, UNIQUE) - Tenant name
- `slug` (VARCHAR 100, UNIQUE, INDEX) - URL-safe identifier
- `description` (VARCHAR 1000) - Description
- `is_active` (BOOL) - Active flag
- `max_monitors` (INT) - Max monitors allowed
- `settings` (JSON) - Tenant-specific settings
- `created_at` (TIMESTAMPTZ) - Record creation
- `updated_at` (TIMESTAMPTZ) - Last update

#### monitor_groups
- `id` (UUID, PK) - Group ID
- `tenant_id` (UUID, FK) - Tenant
- `name` (VARCHAR 255) - Group name
- `description` (VARCHAR 500) - Description
- `created_at` (TIMESTAMPTZ) - Record creation

#### monitors
- `id` (UUID, PK) - Monitor ID
- `tenant_id` (UUID, FK, INDEX) - Tenant
- `group_id` (UUID, FK, NULLABLE) - Group membership
- `agent_id` (UUID, FK, NULLABLE) - Assigned agent
- `name` (VARCHAR 255) - Monitor name
- `type` (ENUM) - ping/http/tcp/snmp/dns/ssl
- `target` (VARCHAR 500) - Target host/URL
- `port` (INT, NULLABLE) - TCP port
- `interval` (INT) - Check interval (seconds)
- `timeout` (INT) - Timeout (seconds)
- `status` (ENUM) - up/down/degraded/paused/pending
- `is_active` (BOOL) - Active flag
- `config` (JSON) - Probe-specific config
- `tags` (JSON) - Tags array
- `last_checked_at` (TIMESTAMPTZ, NULLABLE)
- `last_status_change` (TIMESTAMPTZ, NULLABLE)
- `response_time_ms` (FLOAT, NULLABLE)
- `availability_percentage` (FLOAT, DEFAULT 100)
- `created_at` (TIMESTAMPTZ) - Record creation
- `updated_at` (TIMESTAMPTZ) - Last update

#### checks
- `id` (UUID, PK) - Check ID
- `monitor_id` (UUID, FK, INDEX) - Monitor
- `is_success` (BOOL) - Check result
- `response_time_ms` (FLOAT, NULLABLE)
- `status_code` (INT, NULLABLE)
- `error_message` (TEXT, NULLABLE)
- `metrics_data` (JSON) - Probe metrics
- `created_at` (TIMESTAMPTZ, INDEX) - Timestamp

#### incidents
- `id` (UUID, PK) - Incident ID
- `monitor_id` (UUID, FK, INDEX) - Monitor
- `tenant_id` (UUID, FK, INDEX) - Tenant
- `title` (VARCHAR 255) - Incident title
- `description` (TEXT) - Description
- `severity` (ENUM) - critical/warning/info
- `started_at` (TIMESTAMPTZ, INDEX)
- `resolved_at` (TIMESTAMPTZ, NULLABLE)
- `duration_seconds` (INT, NULLABLE)
- `is_resolved` (BOOL, DEFAULT FALSE, INDEX)

#### notification_channels
- `id` (UUID, PK) - Channel ID
- `tenant_id` (UUID, FK, INDEX) - Tenant
- `user_id` (UUID, FK, NULLABLE) - Owner
- `name` (VARCHAR 255) - Channel name
- `type` (VARCHAR 50) - email/slack/webhook/telegram
- `config` (JSON) - Channel config
- `is_active` (BOOL) - Active flag
- `created_at` (TIMESTAMPTZ)

#### alert_rules
- `id` (UUID, PK) - Rule ID
- `tenant_id` (UUID, FK, INDEX) - Tenant
- `monitor_id` (UUID, FK, NULLABLE) - Linked monitor
- `name` (VARCHAR 255) - Rule name
- `condition` (JSON) - Condition definition
- `for_duration` (INT) - Duration before trigger
- `is_active` (BOOL) - Active flag
- `created_at` (TIMESTAMPTZ)

#### agents
- `id` (UUID, PK) - Agent ID
- `tenant_id` (UUID, FK, INDEX) - Tenant
- `name` (VARCHAR 255) - Agent name
- `version` (VARCHAR 50) - Agent version
- `hostname` (VARCHAR 255) - Hostname
- `ip_address` (VARCHAR 45) - IP address
- `api_key_hash` (VARCHAR 255, UNIQUE) - API key hash
- `is_active` (BOOL) - Active flag
- `is_online` (BOOL, INDEX) - Online flag
- `system_info` (JSON) - System specs
- `last_heartbeat` (TIMESTAMPTZ, NULLABLE)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

#### audit_logs
- `id` (UUID, PK) - Log ID
- `tenant_id` (UUID, FK, INDEX) - Tenant
- `user_id` (UUID, FK, INDEX) - Actor
- `action` (VARCHAR 100, INDEX) - Action type
- `resource_type` (VARCHAR 100) - Resource type
- `resource_id` (VARCHAR 100, NULLABLE)
- `ip_address` (VARCHAR 45, NULLABLE)
- `user_agent` (TEXT, NULLABLE)
- `details` (JSON) - Extra details
- `created_at` (TIMESTAMPTZ, INDEX)

## InfluxDB (Metrics)

### Measurement: `metrics`
- Tags: `monitor_id`, `check_id`, `probe_type`
- Fields: `response_time_ms`, `status_code`, `rtt_ms`, `content_length`
- Timestamp: RFC3339

## Redis (Cache)

| Key Pattern | Value | TTL |
|-------------|-------|-----|
| `session:{token}` | Session data | 30 min |
| `rate_limit:{ip}` | Counter | 60s |