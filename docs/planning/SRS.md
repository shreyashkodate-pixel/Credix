# SmartLoan Predictor — Software Requirements Specification (SRS)

**Document status:** Draft for review  
**Version:** 0.1.0  
**Phase:** 1 — Planning and Requirements  
**Related document:** `PRD.md`

## 1. Purpose

This document defines testable software requirements for SmartLoan Predictor. Requirements depending on the dataset or a later architecture decision are marked **TBD** and must not be implemented through guesswork.

## 2. System context

- **Frontend:** Next.js + TypeScript on Vercel.
- **Backend API:** Python + FastAPI on Render.
- **ML service:** Python + FastAPI, likely on Render (tentative).
- **Database:** PostgreSQL on Supabase.
- **Coding workflow:** Google Antigravity, with phase-specific prompts, human review, tests, and Git version control.
- **Communication:** HTTPS REST APIs in deployed environments. The frontend must not call the ML service or database directly.

## 3. Actors

- **Guest:** can access public pages and registration/sign-in screens.
- **Registered user:** can submit predictions and access only their own history/profile.
- **Administrator:** can access explicitly authorized administrative endpoints and views.
- **Backend service:** validates requests, enforces access control, orchestrates inference, and accesses the database.
- **ML service:** performs validated inference and returns model output, version metadata, and supported explanation data.

## 4. Functional requirements

### Accounts and access control
- **FR-001 — Registration:** The system shall allow a guest to register using the approved account fields. Exact fields and email-verification policy are TBD.
- **FR-002 — Authentication:** The system shall authenticate users using the approved mechanism. Passwords, if used, shall never be stored in plaintext.
- **FR-003 — Sign-out:** The system shall provide a sign-out flow appropriate to the selected session/token strategy.
- **FR-004 — Current user:** An authenticated user shall be able to retrieve their own profile without exposing authentication secrets.
- **FR-005 — Roles:** The system shall distinguish regular users and administrators.
- **FR-006 — Backend authorization:** Every protected backend endpoint shall enforce authorization server-side. Frontend route protection alone is insufficient.
- **FR-007 — Admin provisioning:** Public registration shall not permit a user to self-assign administrator privileges. Admin creation/provisioning process is TBD.

### Prediction
- **FR-008 — Prediction input:** The system shall accept only the input fields approved after the dataset audit. The final schema is TBD.
- **FR-009 — Validation:** The backend shall validate required fields, types, ranges, allowed categories, and cross-field constraints where justified by the data specification.
- **FR-010 — Inference orchestration:** The backend shall call the ML service using a versioned, documented request/response contract.
- **FR-011 — Prediction result:** The system shall return the predicted outcome, model version, and supported explanatory information.
- **FR-012 — Probability display:** A numeric probability may be displayed only if evaluation demonstrates that it is appropriate and its meaning is clearly documented. Otherwise, omit it.
- **FR-013 — Explanation limitations:** The UI shall not describe feature importance or model explanations as proof of causation.
- **FR-014 — Safe failure:** If inference fails or times out, the backend shall return a safe error and shall not create a successful prediction-history record for a failed inference.
- **FR-015 — History persistence:** On successful prediction, the backend shall persist the result and required metadata before representing it as saved.
- **FR-016 — Model traceability:** A prediction record should include the model/artifact version and creation timestamp, along with the inputs and outputs needed for the approved audit policy.
- **FR-017 — Duplicate/retry behavior:** The implementation shall define safe behavior for retried requests to avoid misleading duplicate records. Idempotency strategy is TBD.

### Prediction history
- **FR-018 — Own history:** A registered user shall be able to list and view only their own prediction records.
- **FR-019 — History filtering/pagination:** History endpoints shall use bounded pagination. Sorting/filtering capabilities are TBD.
- **FR-020 — Ownership enforcement:** User identity used for ownership shall come from the authenticated server-side principal, not a client-supplied user ID.
- **FR-021 — Deletion/retention:** The system shall implement the approved retention and deletion policy. Policy is TBD.

### Administration
- **FR-022 — Admin dashboard:** An administrator shall be able to view approved aggregate statistics.
- **FR-023 — User management:** An administrator shall be able to perform only the user-management actions explicitly approved for the MVP.
- **FR-024 — Administrative access:** Unauthorized users shall receive an appropriate denial response for administrative operations.
- **FR-025 — Auditability:** Sensitive administrative actions should be recorded with actor, action, timestamp, and a minimal safe set of metadata. Exact event list is TBD.
- **FR-026 — Data minimization:** Administrative screens shall not expose passwords, tokens, secrets, or unnecessary sensitive applicant details.

### Operations
- **FR-027 — Health check:** Each service shall expose an appropriate health endpoint.
- **FR-028 — Readiness:** The ML service should expose readiness information that indicates whether the required model/artifacts are loaded.
- **FR-029 — Error format:** The backend shall use a consistent documented error response format without stack traces or secrets in production responses.
- **FR-030 — Logging:** Services shall produce useful operational logs while excluding passwords, tokens, secrets, and unnecessary sensitive input data.
- **FR-031 — Configuration:** Environment-specific configuration and secrets shall be injected through environment/secret configuration, not hard-coded.
- **FR-032 — Model compatibility:** The ML service shall validate that the deployed artifact and preprocessing configuration are compatible before accepting inference requests.

## 5. Non-functional requirements

- **NFR-001 Security:** Enforce server-side authorization, secure secret handling, HTTPS in deployed environments, safe CORS policy, input validation, and secure authentication/session practices.
- **NFR-002 Privacy:** Collect only data needed for the approved functionality. Document access, retention, and deletion behavior.
- **NFR-003 Reliability:** Handle unavailable dependencies, invalid inputs, timeouts, and model-load failures without returning fabricated predictions.
- **NFR-004 Maintainability:** Keep frontend, backend, ML inference, and database responsibilities separated and documented.
- **NFR-005 Reproducibility:** Version dataset preparation, training configuration, model artifact, preprocessing, and evaluation results.
- **NFR-006 Testability:** Include automated unit and integration tests, especially for authentication, authorization, validation, history ownership, and inference failure.
- **NFR-007 Accessibility:** Provide semantic controls, labels, keyboard access, visible focus, sufficient contrast, and understandable error messages.
- **NFR-008 Responsive UI:** Core flows shall be usable on mobile and desktop viewports.
- **NFR-009 Observability:** Include health checks, structured logs, and sufficient metadata to diagnose service failures without logging sensitive data.
- **NFR-010 Performance:** Establish measurable latency and throughput targets after selecting the dataset, model, and hosting plans. Do not invent a threshold at this stage.
- **NFR-011 Availability:** Define target availability after hosting tiers and project needs are known.
- **NFR-012 Portability:** Support reproducible local setup and documented online deployment.
- **NFR-013 API consistency:** Document request/response schemas, validation failures, and service errors.
- **NFR-014 Data integrity:** Persist prediction records with referential integrity and consistent model-version metadata.

## 6. Security and privacy requirements

1. No secret, database credential, signing key, or private ML-service token may be committed to Git.
2. Frontend environment variables exposed to browser bundles must contain no secrets.
3. Database access must be server-side; frontend code must never connect directly to PostgreSQL.
4. The backend must be the only public application entry point for prediction operations.
5. The ML service should be private/restricted where supported, or protected with service-to-service authentication.
6. Admin authorization must be checked on each protected endpoint.
7. Logs and error messages must not reveal credentials, stack traces, or unnecessary personal data.
8. User history queries must be scoped by authenticated user identity.
9. Rate limiting and abuse controls should be assessed before public release.
10. Dataset fairness, representativeness, target validity, and limitations must be discussed in the model report.

## 7. Acceptance criteria (MVP)

- Registration/authentication flows pass automated tests.
- A regular user cannot access admin endpoints.
- A user cannot read another user's prediction history by changing request parameters.
- Invalid prediction inputs are rejected by the backend.
- Valid input results are generated by the deployed model pipeline.
- Inference failure or timeout produces a safe error and no successful saved record.
- Stored records include timestamps and model-version metadata.
- Probability estimates are omitted unless validated and appropriately described.
- Secrets are absent from source control and frontend bundles.
- Core user flows work at desktop and mobile widths.
- Automated test and deployment instructions are documented.
- Dataset provenance, license, target definition, model evaluation, and limitations are documented.

## 8. TBD decisions

- Dataset, target label, and final input schema
- Authentication/session strategy
- Email verification and password reset requirements
- Exact role/permission matrix and admin provisioning
- Explanation method and whether probability values are supportable
- Database schema details and retention/deletion policy
- API versioning and error envelope details
- Rate limits, performance targets, availability targets
- Model artifact delivery and deployment process
- Render service plan and ML hosting confirmation
