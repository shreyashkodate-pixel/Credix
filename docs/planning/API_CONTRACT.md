# SmartLoan Predictor — API Contract Draft

**Document status:** Updated specification; endpoints and finalized Phase 2 input schema  
**Version:** 0.2.0  
**Phase:** 2 — Dataset Selection, Audit, and Licensing (Schema Approved)

## 1. Purpose and status

This document defines the initial API boundary between the frontend, backend, and ML service. Endpoint paths and payloads are proposals, not implemented contracts. Final prediction fields depend on the dataset audit and model design. Do not generate production code from TBD fields as though they were confirmed.

## 2. API principles

- The browser calls the backend API only.
- The backend is responsible for authentication, authorization, validation, orchestration, and database persistence.
- The ML service is called by the backend, not directly by the browser.
- Deployed communication uses HTTPS.
- JSON is the default request/response format.
- Request schemas are validated server-side.
- Errors must be predictable and must not expose stack traces or secrets.
- Use a versioning approach before the API is treated as stable; whether to use `/api/v1` is TBD.

## 3. Proposed backend endpoints

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/auth/register` | Guest | Create a user account |
| POST | `/auth/login` | Guest | Authenticate |
| POST | `/auth/logout` | Authenticated | End session/revoke relevant credentials |
| GET | `/users/me` | Authenticated | Retrieve current user's profile |
| POST | `/predictions` | Authenticated | Validate input, invoke ML, persist result |
| GET | `/predictions/history` | Authenticated | List own prediction history |
| GET | `/predictions/history/{prediction_id}` | Authenticated | Retrieve one owned prediction |
| GET | `/admin/dashboard` | Admin | Retrieve permitted aggregate metrics |
| GET | `/admin/users` | Admin | List users with bounded pagination and minimal fields |
| PATCH | `/admin/users/{user_id}` | Admin | Approved user-management operation; exact fields TBD |
| GET | `/health` | Public/minimal | Backend liveness check |

The final admin operations, rate limits, pagination parameters, and authentication mechanism require approval.

## 4. Proposed ML endpoints

| Method | Path | Caller | Purpose |
|---|---|---|---|
| POST | `/predict` | Backend service only | Run model inference |
| GET | `/health` | Platform/monitoring | Process liveness |
| GET | `/ready` | Backend/platform | Confirm model and required artifacts are loaded |

ML endpoints should not be exposed as an unrestricted public prediction API. Protect the service using private networking where available and/or service-to-service authentication.

## 5. Confirmed prediction request schema

The model input schema was finalized in Phase 2 ([`docs/data/DATASET_AUDIT.md`](../data/DATASET_AUDIT.md)) and approved under [`D-023`](DECISION_REGISTER.md). Demographic attributes (`gender`, `married`) are strictly excluded for Fair Lending compliance.

### 5.1 Request Body (`POST /predictions`)

```json
{
  "applicant_income": 5000.0,
  "coapplicant_income": 1500.0,
  "loan_amount": 120.0,
  "loan_amount_term": 360,
  "credit_history": 1,
  "education": "Graduate",
  "self_employed": "No",
  "dependents": "0",
  "property_area": "Semiurban"
}
```

### 5.2 Field Validation Rules (Backend Pydantic Model)

| Field | Type | Validation Rules | Error Code / Message |
|---|---|---|---|
| `applicant_income` | Float | `> 0.0` | `Must be greater than 0` |
| `coapplicant_income` | Float | `>= 0.0` (defaults to 0.0) | `Must be greater than or equal to 0` |
| `loan_amount` | Float | `> 0.0` (in thousands of dollars) | `Must be greater than 0` |
| `loan_amount_term` | Int | Value in `[12, 36, 60, 120, 180, 240, 300, 360, 480]` | `Invalid loan term duration` |
| `credit_history` | Int | Value in `[0, 1]` | `Must be 1 (meets criteria) or 0 (does not meet)` |
| `education` | String | Value in `["Graduate", "Not Graduate"]` | `Must be 'Graduate' or 'Not Graduate'` |
| `self_employed` | String | Value in `["Yes", "No"]` | `Must be 'Yes' or 'No'` |
| `dependents` | String | Value in `["0", "1", "2", "3+"]` | `Must be '0', '1', '2', or '3+'` |
| `property_area` | String | Value in `["Urban", "Semiurban", "Rural"]` | `Must be 'Urban', 'Semiurban', or 'Rural'` |

Rules:
- Protected demographic fields (`gender`, `married`, `race`, etc.) are prohibited. The backend must ignore or reject unexpected demographic fields.
- Frontend validation is provided for user feedback; backend Pydantic validation is strictly authoritative.
- Failed validation returns `422 Unprocessable Entity` with field-level details.
- User ID is derived from the authenticated session/token, never accepted in the request body.

## 6. Proposed prediction response

The response shape below is illustrative. Final fields depend on the chosen model and explanation method.

```json
{
  "prediction_id": "server-generated-id",
  "outcome": "model-defined-label",
  "explanation": {
    "method": "documented-method",
    "factors": []
  },
  "probability": null,
  "model_version": "version-string",
  "created_at": "ISO-8601 timestamp"
}
```

- `outcome` must use the target labels defined by the audited dataset and approved user-facing wording.
- `explanation` must accurately describe the chosen method and avoid causal claims.
- `probability` must be absent or null unless validated and appropriate to expose. If exposed, define exactly what it means and document calibration/limitations.
- `model_version` is required for traceability.
- The backend must not trust an arbitrary model version sent by the browser.

## 7. Proposed history response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

This is a proposed pagination envelope. The implementation must enforce a maximum page size and derive ownership from the authenticated principal. Exact history item fields are TBD after the database and privacy policy are approved.

## 8. Proposed error response

A consistent envelope should be selected before implementation. Candidate:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields.",
    "details": []
  },
  "request_id": "correlation-id"
}
```

Possible error classes:
- invalid request/validation error;
- unauthenticated;
- forbidden;
- resource not found;
- rate limited;
- inference unavailable or timed out;
- internal server error.

Do not expose stack traces, database details, credentials, internal URLs, or raw exception text in production responses. Exact HTTP status mapping is TBD.

## 9. Authentication contract decision

Not yet selected:
- secure cookie-based session, or
- JWT access/refresh token strategy.

The final contract must document cookie flags/CSRF protections or token storage/refresh/revocation behavior, depending on the chosen approach. Do not implement a hybrid accidentally.

## 10. Backend-to-ML contract

The backend should send only the validated fields required for inference. The internal request should include a contract version or equivalent compatibility mechanism.

The ML service response should include:
- predicted outcome;
- model version;
- explanation data supported by the model;
- probability only if the agreed evaluation supports it;
- structured error information for invalid payloads, model-not-ready state, or inference failure.

The backend must validate the ML response before persisting it. Use a bounded timeout. Never convert a timeout or malformed response into a fabricated prediction.

## 11. Contract testing requirements

- Validate request and response schemas.
- Test missing, malformed, out-of-range, and unsupported fields.
- Test unauthenticated and unauthorized access.
- Test user-history ownership and admin restrictions.
- Test ML timeout, unavailable service, invalid response, and model-not-ready behavior.
- Test that failed inference does not create a successful prediction record.
- Keep OpenAPI documentation aligned with implemented schemas.
- Add contract/version compatibility tests between backend and ML service.

## 12. Open items

- API prefix/versioning convention.
- Authentication strategy and exact auth payloads.
- Final prediction input and target labels.
- Final explanation payload and probability policy.
- Error envelope and status-code mapping.
- Pagination and filtering details.
- Idempotency behavior for prediction submissions.
- Service-to-service authentication mechanism.
