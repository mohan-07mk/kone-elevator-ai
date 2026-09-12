# Supabase Production Readiness & Integration Guide

## Executive Summary
This document provides a comprehensive audit and step-by-step readiness guide for connecting the Elevator AI FastAPI backend to an existing external Supabase PostgreSQL database.

---

## 1. Integration Status
- **Backend Architecture**: FastAPI (async) with SQLAlchemy 2.0 and Alembic schema management.
- **Database Driver**: `postgresql+asyncpg` for async API endpoints; standard `postgresql` for Alembic migrations.
- **URL Protocol Normalization**: Automatically converts incoming `postgres://` and `postgresql://` connection strings to `postgresql+asyncpg://` for async SQLAlchemy engine sessions.
- **PgBouncer / Transaction Pooler Compatibility**: Automatically sets `statement_cache_size = 0` when connecting via Supabase transaction poolers (`port 6543` or `*.pooler.supabase.com`).

---

## 2. Database URL Configuration
Supabase provides two primary connection strings in the Supabase Dashboard (`Project Settings -> Database`):

### Direct Connection (Port 5432)
```text
postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres?sslmode=require
```

### Transaction Pooler Connection (Port 6543 - Recommended for Serverless/Scale)
```text
postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
```

> **Note**: Both connection string formats are supported seamlessly. The backend automatically injects driver protocols and pooler settings without requiring manual code modifications.

---

## 3. Migration Status
- **Schema Management**: Managed exclusively via Alembic (`backend/migrations/versions/`).
- **Initial Migration**: `db30183c0752_initial_schema.py` contains all required table, index, constraint, and foreign key definitions.
- **Production Lifespan**: Production application startup (`DEBUG=false`) does not invoke `Base.metadata.create_all()`.

---

## 4. Expected Database Tables (18 Total)
The migration script provisions the following 18 tables:

1. `buildings` — Building locations and metadata
2. `roles` — System roles (Admin, Maintenance Engineer, Manager, Technician)
3. `users` — Registered users and password hashes
4. `elevators` — Elevator fleet state, health score, and risk level
5. `sensor_definitions` — Telemetry sensor catalog and normal ranges
6. `ai_inferences` — AI fault classification model outputs
7. `alert_records` — Active and historical system alerts
8. `audit_logs` — System audit and user action logs
9. `devices` — Edge hardware gateways (STM32/Raspberry Pi)
10. `elevator_health_records` — Explainable health breakdowns
11. `predictive_records` — RUL (Remaining Useful Life) estimations
12. `sensor_readings` — Time-series sensor telemetry data
13. `system_settings` — Platform thresholds and runtime configuration
14. `technicians` — Technician profiles, ratings, and workload
15. `threshold_configs` — Warning and critical alert thresholds
16. `user_preferences` — UI theme and notification preferences
17. `maintenance_tasks` — Work orders and AI task assignments
18. `rca_results` — Root Cause Analysis reports and evidence

---

## 5. Seed Status
- **Implementation**: `backend/app/database/seed.py`
- **Idempotency**: All seed insertion logic queries existing keys/IDs before inserting. Re-running seed logic in production produces **0 duplicate records** and **0 data deletions**.

---

## 6. Required Environment Variables for Production

Configure the following environment variables in your deployment host (e.g. Render / Supabase Host):

```env
DEBUG=false
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
JWT_SECRET_KEY=<GENERATE_A_STRONG_RANDOM_64_CHAR_SECRET>
ADMIN_PASSWORD=<GENERATE_A_SECURE_ADMIN_PASSWORD>
CORS_ORIGINS=https://<your-netlify-app>.netlify.app
```

---

## 7. Commands to Apply Migrations to Supabase

To apply the database schema to your Supabase PostgreSQL database from a terminal:

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Set your Supabase connection string environment variable
$env:DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres?sslmode=require"

# 3. Run Alembic migration to create all 18 tables
python -m alembic upgrade head
```

---

## 8. Risks & Considerations
1. **Network Connectivity & SSL**: Supabase requires SSL for remote connections. Ensure `?sslmode=require` is appended to your connection string.
2. **Prepared Statements on PgBouncer**: If using port `6543` (Transaction Pooler), asyncpg prepared statements are disabled automatically via `statement_cache_size = 0` to prevent PgBouncer transaction mode errors.
3. **Secret Security**: Never commit actual database passwords or JWT secret keys to version control. Keep all credentials in deployment environment settings.
