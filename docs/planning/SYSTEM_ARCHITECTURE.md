# SmartLoan Predictor — System Architecture Specification

**Document status:** Draft for review  
**Version:** 0.1.0  
**Phase:** 1 — Planning and Requirements

## 1. Architecture summary

SmartLoan Predictor uses three application services and one managed database service:

1. Next.js + TypeScript frontend — Vercel.
2. FastAPI backend API — Render.
3. FastAPI ML inference service — likely Render; not final.
4. PostgreSQL database — Supabase.

The frontend must not connect directly to PostgreSQL or the ML service. The backend owns authentication, authorization, business rules, data persistence, and orchestration. The ML service owns model inference and model-specific preprocessing/explanation logic.

## 2. Logical architecture

```text
Browser
  |
  | HTTPS
  v
Next.js Frontend (Vercel)
  |
  | HTTPS REST API
  v
Backend API (FastAPI on Render)
  |                         |
  | SQL / approved DB       | authenticated internal HTTP request
  v                         v
Supabase PostgreSQL      ML Service (FastAPI; likely Render)
                             |
                             v
                     Model + preprocessing artifact
```

The diagram is logical, not a final network topology. Exact Render private-network support, service-to-service routing, Supabase connectivity, and hosting plan limitations must be verified before deployment.

## 3. Service responsibilities

### 3.1 Frontend
- Render public pages, registration/sign-in, prediction form, result, history, and admin views.
- Provide client-side usability validation but rely on backend validation for enforcement.
- Call only the backend API for protected application operations.
- Handle loading, empty, success, validation, and service-error states.
- Use public configuration only for values safe to expose to the browser, such as the backend base URL.
- Never store database credentials or ML-service secrets in client-side code.

### 3.2 Backend API
- Own registration, authentication, session lifecycle, roles, and authorization.
- Validate and normalize request payloads.
- Enforce per-user history ownership and admin permissions.
- Call the ML service using a documented contract and bounded timeout.
- Persist successful predictions and required metadata in PostgreSQL.
- Expose prediction history and approved administrative endpoints.
- Provide consistent errors, health checks, and safe operational logs.
- Manage database migrations through a documented migration tool selected during implementation.
- Be the only service that performs application database operations.

### 3.3 ML service
- Load a versioned model and its matching preprocessing pipeline.
- Validate incoming inference payloads against the model contract.
- Return a predicted class/outcome and supported explanation data.
- Return model version and relevant metadata.
- Expose health/readiness checks.
- Fail clearly when model artifacts are missing or incompatible.
- Avoid database access, user authentication ownership, and history persistence.
- Be restricted to backend-originated calls where the hosting platform permits it; otherwise use service authentication and network controls.

### 3.4 PostgreSQL (Supabase)
- Store account records and approved profile fields.
- Store prediction history and model-version metadata.
- Store approved audit events.
- Enforce primary keys, foreign keys, uniqueness, and useful indexes.
- Be reachable only from trusted server-side services.
- Use migrations as the source of truth for schema changes.
- Do not rely on client-side access controls as a replacement for backend authorization.

## 4. Main request flows

### 4.1 Prediction flow
1. Browser submits the form to the backend.
2. Backend authenticates the caller and validates fields.
3. Backend sends the validated payload to the ML service.
4. ML service performs inference using the matching preprocessing pipeline.
5. ML service returns a versioned result and supported explanation.
6. Backend validates the ML response and persists the successful result.
7. Backend returns the result and history identifier to the frontend.
8. Frontend displays the result and indicates whether it was saved.

If inference fails, times out, or returns an invalid response, do not create a successful prediction record. If persistence fails, do not tell the user that the result was successfully saved. The final retry/transaction semantics must be defined in implementation.

### 4.2 History flow
1. Browser requests the signed-in user's history.
2. Backend derives user identity from the authenticated principal.
3. Backend queries only records owned by that identity.
4. Backend returns bounded, paginated results.

A client-provided user ID must never be trusted as the basis for access to history.

### 4.3 Admin flow
1. Administrator signs in.
2. Backend validates administrator privileges for each admin operation.
3. Backend retrieves only approved metrics/records.
4. Sensitive operations are logged using the approved audit policy.

## 5. Proposed API areas

Exact schemas and error envelopes are specified later in `API_CONTRACT.md`. Initial endpoint candidates:

### Backend API
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /users/me`
- `POST /predictions`
- `GET /predictions/history`
- `GET /predictions/history/{prediction_id}`
- `GET /admin/dashboard`
- `GET /admin/users`
- Approved admin user-management routes, TBD
- `GET /health`

### ML service
- `POST /predict`
- `GET /health`
- `GET /ready`

These are proposed paths, not implemented or final.

## 6. Technology and deployment decisions

| Layer | Selected technology/provider | Status |
|---|---|---|
| Frontend | Next.js + TypeScript / Vercel | Selected |
| Backend API | Python + FastAPI / Render | Selected |
| ML inference | Python + FastAPI + scikit-learn / likely Render | Tentative provider |
| Database | PostgreSQL / Supabase | Selected |
| Local orchestration | Docker Compose | Proposed; validate before adopting |
| Version control | Git + GitHub | Selected workflow |

## 7. Configuration and secrets

- Maintain safe example configuration in `.env.example` with placeholders only.
- Keep real secrets in local untracked environment files or provider secret stores.
- Use separate configuration for development, test, and production.
- Backend database credentials remain server-side.
- ML-service authentication material remains server-side and must not be included in frontend bundles.
- Validate required environment variables at startup and fail with a safe, actionable message if required configuration is missing.
- Never log secret values.

## 8. Reliability and operations

- Use explicit timeouts for backend-to-ML requests.
- Avoid unbounded retries that could create duplicate records or overload a service.
- Provide health endpoints and an ML readiness endpoint.
- Distinguish service liveness from readiness to serve predictions.
- Log request correlation identifiers and service errors without logging credentials or unnecessary personal data.
- Handle model artifact loading failures as a readiness failure.
- Define latency and resource targets after measuring the selected model and hosting plans.

## 9. ML artifact lifecycle

- Dataset provenance, license, cleaning, split strategy, and target definition must be documented.
- Training and inference must use compatible preprocessing.
- Store model artifact version, training code/configuration version, and evaluation report.
- Avoid loading untrusted serialized artifacts.
- A model update should be evaluated and tested before production replacement.
- The model must not be retrained automatically in the live request path.
- Retraining cadence and approval workflow are TBD.

## 10. Architecture risks and mitigations

| Risk | Mitigation |
|---|---|
| ML service publicly callable | Restrict network access where possible; otherwise use service authentication and request validation |
| Model and preprocessing mismatch | Version and package them together; add compatibility checks |
| Cold starts or memory constraints | Benchmark on Render plan; compare alternatives if needed |
| Sensitive data leakage in logs | Structured logging with redaction and data minimization |
| Unauthorized history access | Derive ownership from authenticated identity and test cross-user access |
| Dataset bias or misleading target | Audit provenance, label meaning, representativeness, and limitations |
| Frontend accidentally exposes secrets | Keep private configuration in backend only; inspect production bundle/config |
| Schema drift | Use versioned migrations and tests |

## 11. Open architecture decisions

- Authentication: secure cookie session versus JWT access/refresh.
- Exact database schema and migration tool.
- Service-to-service authentication/network topology on Render.
- API versioning and common error response format.
- ML artifact storage/delivery and model-loading strategy.
- Final Render plan and ML hosting confirmation.
- Observability, rate limiting, and quantitative SLOs.
