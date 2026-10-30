# Credix — Technical Debt & Architectural Deferred Items

**Document Status:** Living Register  
**Baseline Version:** 0.5.0  
**Last Updated:** 2026-10-30  
**Related Documents:** [`docs/planning/DECISION_REGISTER.md`](docs/planning/DECISION_REGISTER.md), [`docs/data/DATASET_AUDIT.md`](docs/data/DATASET_AUDIT.md), [`ml/README.md`](ml/README.md), [`backend/README.md`](backend/README.md)

---

## 1. Overview & Strategy

Technical debt in Credix is divided into two categories:
1. **Intentional Deferred Decisions**: Architectural or implementation choices intentionally postponed to preserve phased discipline (e.g., waiting for the dataset audit before defining column types).
2. **Provisional Scaffolding Debt**: Temporary placeholders or simplified contracts that must be hardened before public deployment (e.g., provisional environment templates, tentative hosting providers).

This register documents every known area of technical debt, its current status, associated risks, and the targeted resolution phase.

---

## 2. Technical Debt Register

| ID | Category | Item | Current Status | Risk / Impact | Target Phase |
|---|---|---|---|---|---|
| **TD-001** | Configuration | Service-specific `.env.example` templates | **Resolved in Phase 5** | Both `backend/.env.example` and `frontend/.env.example` templates completed. | Phase 5 |
| **TD-002** | API Design | API versioning prefix (`/api/v1`) | **Resolved in Phase 4** (`D-029`) | Versioned API router standardized across all endpoints. | Phase 4 |
| **TD-003** | Security / Auth | Auth strategy: JWT Bearer Tokens | **Resolved in Phase 4** (`D-030`) | Standard Bearer JWT tokens implemented with native `bcrypt` password hashing. | Phase 4 |
| **TD-004** | Security / Auth | Admin user provisioning & RBAC boundaries | **Resolved in Phase 4** (`D-031`) | RBAC implemented with `admin` vs `user` roles and `get_current_admin` guard. | Phase 4 |
| **TD-005** | Database | Database ORM & migration framework | **Resolved in Phase 4** (`D-032`) | SQLAlchemy 2.0 ORM + Alembic migrations (`001_initial_schema.py`) implemented. | Phase 4 |
| **TD-006** | Database | Primary key strategy (UUID vs BigInt) | **Resolved in Phase 4** (`D-033`) | UUID primary keys standardized across `users`, `predictions`, `audits`. | Phase 4 |
| **TD-007** | Database | Typed columns vs JSON for inputs & explanations | **Resolved in Phase 4** (`D-034`) | Hybrid model: typed metadata columns + JSONB inputs & TreeSHAP attributions. | Phase 4 |
| **TD-008** | Infrastructure | ML Service hosting & colocation topology | Open Decision (`O-014`) | Evaluation of colocated Python inference vs standalone Render service. | Phase 6 |
| **TD-009** | Infrastructure | Backend-to-ML Service private networking vs Token Auth | Open Decision (`O-013`) | Relevant if standalone microservice is chosen; bypassable if colocated. | Phase 6 |
| **TD-010** | ML Pipeline | Target label ambiguity & data leakage risk | **Resolved in Phase 2** (`D-021`, `D-022`, `D-023`) | Target grounded as `Loan_Status`; demographic attributes permanently excluded. | Phase 2 |
| **TD-011** | ML Pipeline | Model explainability technique unbenchmarked | **Resolved in Phase 3** (`D-026`) | TreeSHAP achieves sub-15ms local attribution without slow sampling. | Phase 3 |
| **TD-012** | ML Pipeline | Probability calibration policy undefined | **Resolved in Phase 3** (`D-027`) | Brier score (0.1513) confirms reliability of raw probabilities. | Phase 3 |
| **TD-013** | Operations | Error envelope & Request ID correlation format | **Hardened in Phase 4.2** (`D-035`) | Standard JSON error envelope unified across all HTTP errors (400, 401, 403, 404, 422, 500) and persisted to `PredictionRecord.request_id`. | Phase 4.2 |
| **TD-014** | Governance | Data retention & cascade deletion policy | **Resolved in Phase 4** (`D-036`) | `ondelete="CASCADE"` foreign keys configured on predictions and audit events. | Phase 4 |
| **TD-015** | Database | Live Supabase PostgreSQL Verification | Deferred to Phase 6 | Migrations currently verified against SQLite only; live PostgreSQL connection pooling, SSL, and dialect verification required before deployment. | Phase 6 |

---

## 3. Detailed Debt Descriptions & Resolutions

### TD-001: Service-Specific Environment Templates (RESOLVED — Phase 5)
- **Status:** Resolved in Phase 5.
- **Resolution:** Created [`backend/.env.example`](backend/.env.example) detailing `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, and `ML_ARTIFACTS_DIR`. Created [`frontend/.env.example`](frontend/.env.example) configuring `NEXT_PUBLIC_API_URL` for FastAPI backend communication.

### TD-002: API Versioning Prefix (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-029`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Standardized all business endpoints under `/api/v1/*` (`/api/v1/auth`, `/api/v1/predictions`, `/api/v1/admin`) with root `/health` liveness probe.

### TD-003: Authentication Strategy (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-030`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Implemented JWT Bearer token authentication utilizing `pyjwt` and native `bcrypt` password hashing (truncated to 72 bytes safely). Expiration defaults to 24 hours (1440 minutes).

### TD-004: Admin Provisioning & RBAC Boundaries (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-031`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Implemented role-based access control with `user` and `admin` roles. Endpoints `/api/v1/admin/dashboard` and `/api/v1/admin/users` require the `get_current_admin` FastAPI dependency, returning `403 Forbidden` for non-admin accounts.

### TD-005: Database ORM & Migration Framework (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-032`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Implemented SQLAlchemy 2.0 with Alembic. Authored initial migration revision [`001_initial_schema.py`](backend/alembic/versions/001_initial_schema.py) defining tables, foreign keys, and indexes. Tested successfully against SQLite dev fallback and Supabase PostgreSQL schema.

### TD-006: Primary Key Strategy (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-033`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Standardized UUID strings (`CHAR(36)` / `UUID`) generated via Python `uuid.uuid4()` as primary keys across all database tables.

### TD-007: JSON Storage for Inputs & Explanations (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-034`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Standardized a hybrid design: relational columns for queryable metadata (`id`, `user_id`, `created_at`, `model_version`, `outcome`, `probability`) and JSON/JSONB columns for applicant input snapshots and TreeSHAP attribution objects.

### TD-013: Standardized Error Envelopes & Correlation IDs (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-035`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Built `RequestCorrelationMiddleware` injecting `X-Request-ID` and `X-Response-Time-Ms` response headers. Added custom FastAPI `RequestValidationError` handler returning unified `{ "error": { "code": ..., "message": ..., "details": ... }, "request_id": ... }`.

### TD-014: Data Retention & Cascade Deletion Policy (RESOLVED — Phase 4)
- **Status:** Resolved in Phase 4 via [`D-036`](docs/planning/DECISION_REGISTER.md).
- **Resolution:** Configured `ondelete="CASCADE"` on all user foreign keys in `prediction_records` and `audit_events`.

---

## 4. Maintenance Guidelines

1. **Review Frequency:** Update this document at the start and end of every development phase.
2. **Resolution Tracking:** When a technical debt item is resolved, record the resolving commit, mark status as `Resolved`, and update associated documentation.
3. **No Hidden Debt:** If a temporary workaround or stub is introduced in code, immediately log a new `TD-xxx` entry in this register.
