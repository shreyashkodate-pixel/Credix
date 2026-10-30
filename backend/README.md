# Credix — Backend API & Database Service

The **Credix Backend** is a high-performance, asynchronous REST API service built with **FastAPI**, **SQLAlchemy 2.0**, and **Alembic**, backed by **Supabase PostgreSQL** and integrated with the Credix champion ML inference pipeline.

---

## 1. Architectural Highlights & Guardrails

- **Decoupled Architecture (`D-004`, `FR-004`):** Browser clients communicate exclusively with the Backend API over HTTPS. Neither Supabase PostgreSQL nor internal ML inference components are directly exposed to the internet.
- **Fair Lending Policy Enforcement (`D-023`):** Prohibited demographic attributes (`Gender`, `Married`, `Race`, `Sex`) are strictly rejected at the API schema boundary (`422 Unprocessable Content`). They are never parsed, processed, or persisted.
- **Strict Ownership Scoping (`D-016`, `FR-018`):** All prediction history operations (`GET /api/v1/predictions/history`, `GET /api/v1/predictions/history/{id}`) are filtered strictly by the authenticated server-side user identity (`user_id`). A user can never view or enumerate another applicant's prediction records.
- **Atomic Persistence (`FR-014`):** Predictions and their corresponding audit trails are saved atomically within a database transaction. If the ML inference engine fails or times out, the database transaction is rolled back, leaving zero uncommitted or orphaned records.
- **Explainability Integration:** Every prediction payload returns local feature attribution weights and human-friendly factor summaries generated via TreeSHAP.
- **Request Traceability (`FR-029`):** Every HTTP request is tagged with an authoritative, trusted server-generated `X-Request-ID` and profiled with `X-Response-Time-Ms`. The request ID is persisted alongside predictions in `PredictionRecord.request_id` for end-to-end tracing.
- **Standardized Error Envelopes (`P-005`):** All application-generated HTTP errors (400, 401, 403, 404, 422, 500) follow a unified JSON envelope: `{"error": {"code": "...", "message": "...", "details": [...]}, "request_id": "..."}`.
- **Security Audit Trails:** Security-relevant events (`AUTH_REGISTER`, `AUTH_LOGIN_SUCCESS`, `AUTH_LOGIN_FAILURE`, `ADMIN_DASHBOARD_ACCESS`, `ADMIN_USERS_LIST_ACCESS`) are recorded in `audit_events` with strict secret/credential scrubbing.
- **OWASP Security Headers:** All responses include `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-XSS-Protection: 1; mode=block`, and conditional HSTS when served over HTTPS.

---

## 2. Directory Layout

```
backend/
├── alembic/                      # Database migration scripts
│   ├── env.py                    # Alembic execution environment
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Versioned migration revisions
│       └── 001_initial_schema.py # Initial DDL: users, predictions, audits
├── alembic.ini                   # Alembic configuration
├── app/
│   ├── api/
│   │   ├── deps.py               # Dependency injection (Auth, Roles, DB session)
│   │   └── v1/
│   │       ├── router.py         # Consolidated API v1 router
│   │       └── endpoints/
│   │           ├── auth.py       # POST /register, POST /login, GET /me, POST /logout
│   │           ├── predictions.py# POST /predictions, GET /history, GET /history/{id}
│   │           ├── admin.py      # GET /admin/dashboard, GET /admin/users
│   │           └── health.py     # GET /health, GET /api/v1/health
│   ├── core/
│   │   ├── config.py             # Pydantic Settings & environment config
│   │   ├── database.py           # SQLAlchemy 2.0 Engine & SessionLocal
│   │   └── security.py           # bcrypt password hashing & JWT handling
│   ├── models/                   # SQLAlchemy ORM Data Models
│   │   ├── user.py               # User entity (UUID, email, hashed_password, role)
│   │   ├── prediction.py         # PredictionRecord entity (JSONB inputs, outputs, SHAP)
│   │   └── audit.py              # AuditEvent entity (actor, event_type, metadata)
│   ├── schemas/                  # Pydantic v2 Request/Response Contracts
│   │   ├── auth.py               # Auth schemas (UserCreate, UserResponse, Token)
│   │   └── prediction.py         # 9-feature loan application & SHAP explanation schemas
│   ├── services/
│   │   └── ml_service.py         # ML inference bridge & atomic persistence
│   └── main.py                   # FastAPI application entrypoint & middleware
├── tests/
│   └── test_backend_api.py       # End-to-end API integration tests
├── requirements.txt              # Production Python dependencies
└── .env.example                  # Environment variable reference template
```

---

## 3. Environment Configuration

Create a `.env` file in the `backend/` directory or root workspace by copying `.env.example`:

```bash
cp backend/.env.example backend/.env
```

Key configuration variables:

| Variable | Description | Default / Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string (Supabase) | `sqlite:///./credix_dev.db` (local fallback) |
| `SECRET_KEY` | Secret key for signing JWT tokens | `credix-super-secure-production-secret-key-change-me` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration | `1440` (24 hours) |
| `CORS_ORIGINS` | Allowed frontend origins (JSON array) | `["http://localhost:3000", "http://127.0.0.1:3000"]` |
| `ML_ARTIFACTS_DIR` | Path to ML model & metadata artifacts | `ml/inference/artifacts` |

---

## 4. Setup & Database Migrations

### A. Virtual Environment Setup
Ensure virtual environment is active and dependencies are installed:

```bash
pip install -r backend/requirements.txt
```

### B. Run Alembic Migrations
Run database migrations to initialize tables (`users`, `prediction_records`, `audit_events`):

```bash
# From workspace root
alembic -c backend/alembic.ini upgrade head
```

---

## 5. Running the Development Server

Start the FastAPI application with auto-reloading enabled:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive OpenAPI Docs (Swagger UI):** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc Documentation:** [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 6. API Endpoints Overview

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/health` | Public | Liveness probe: checks DB connection and ML model status |
| `POST` | `/api/v1/auth/register` | Public | Register new applicant account (default role: `user`) |
| `POST` | `/api/v1/auth/login` | Public | Authenticate with email/password; returns JWT bearer token |
| `GET` | `/api/v1/auth/me` | Authenticated | Retrieve current user profile |
| `POST` | `/api/v1/auth/logout` | Authenticated | Terminate session / token invalidation notice |
| `POST` | `/api/v1/predictions` | Authenticated | Submit 9-feature loan application; runs inference & SHAP |
| `GET` | `/api/v1/predictions/history` | Authenticated | Retrieve paginated prediction history for current user |
| `GET` | `/api/v1/predictions/history/{id}` | Authenticated | Retrieve detailed prediction record by ID (ownership enforced) |
| `GET` | `/api/v1/admin/dashboard` | Admin Only | Global metrics: user counts, total predictions, approval rate |
| `GET` | `/api/v1/admin/users` | Admin Only | Paginated list of registered users and roles |

---

## 7. Running Integration Tests

The test suite validates the entire API stack end-to-end, including authentication, Fair Lending rejection, TreeSHAP inference, ownership scoping, and admin role boundaries:

```bash
PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/matplotlib pytest backend/tests/test_backend_api.py -v
```

