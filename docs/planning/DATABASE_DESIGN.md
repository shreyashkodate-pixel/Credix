# SmartLoan Predictor — Database Design Draft

**Document status:** Conceptual draft; schema not finalized  
**Version:** 0.1.0  
**Database:** PostgreSQL hosted by Supabase

## 1. Design principles

- The backend is the only application component that accesses the database.
- Use migrations as the version-controlled source of truth.
- Enforce data integrity with primary keys, foreign keys, uniqueness, and constraints.
- Derive record ownership from the authenticated backend identity.
- Store only data required for functionality, auditability, and the approved retention policy.
- Do not store passwords in plaintext or store access tokens as ordinary profile fields.
- Final prediction fields depend on the audited dataset and model contract.

## 2. Proposed entities

### 2.1 `users`
Purpose: account identity, profile, role, and account lifecycle.

Proposed fields:
- `id` — primary key; UUID is a candidate.
- `email` — unique normalized email, if email is selected as the account identifier.
- `password_hash` — only if the application manages passwords directly; use a suitable password hashing scheme.
- `role` — constrained value such as `user` or `admin`.
- `is_active` — account state.
- `created_at`, `updated_at` — timestamps.
- `last_login_at` — optional operational metadata.

Do not expose `password_hash` or authentication internals in API responses. Email verification, password reset, and account recovery details are TBD.

### 2.2 `prediction_records`
Purpose: persist successful model predictions for user history and traceability.

Proposed fields:
- `id` — primary key.
- `user_id` — foreign key to `users.id`, not nullable for user-submitted predictions.
- `created_at` — server-generated timestamp.
- `model_version` — version of the model artifact used.
- `outcome` — model-defined target label.
- `probability` — nullable; include only if validated and useful.
- `explanation` — structured JSON or normalized related records, decision TBD.
- `input_snapshot` — JSON or typed columns, depending on final input schema and privacy review.
- `request_id` — optional correlation/idempotency reference, with appropriate constraints if adopted.

Only successfully completed predictions should be stored as successful prediction records. The exact policy for storing failed attempts or operational failures is TBD; avoid retaining raw sensitive inputs in error logs.

### 2.3 `audit_events` (proposed)
Purpose: record selected security-sensitive administrative actions and relevant system events.

Proposed fields:
- `id` — primary key.
- `actor_user_id` — nullable foreign key if events may be system-generated or the actor may later be deleted; policy TBD.
- `event_type` — constrained event name.
- `target_type`, `target_id` — optional target reference.
- `created_at` — server-generated timestamp.
- `metadata` — minimal JSON metadata that must not contain secrets or unnecessary personal data.

Define event categories, retention, and access controls before implementing. Do not log passwords, tokens, secret values, or complete applicant payloads by default.

## 3. Relationships

```text
users 1 -------- * prediction_records
users 1 -------- * audit_events (as actor, optional)
```

A user can have many prediction records. Audit-event relationships depend on the final account-deletion and retention policy.

## 4. Index and constraint candidates

- Unique index on normalized email, if email/password accounts are chosen.
- Index on `prediction_records(user_id, created_at DESC)` for private paginated history.
- Index on `prediction_records(model_version)` if operational reporting requires it.
- Index on `audit_events(created_at DESC)` and/or event type as justified by queries.
- Foreign keys with explicit deletion behavior.
- Check constraints for role/outcome fields where appropriate.
- Avoid indexing every field without a query/use-case reason.

## 5. Ownership and authorization

- Backend queries for user history must scope by the authenticated user's ID.
- Never trust a user ID provided by the browser to decide which records a user may read.
- Admin access must be explicit, server-enforced, and tested.
- If Supabase Row Level Security is used, policies must be designed and tested deliberately; it does not remove the need for backend authorization.
- Database credentials must not be included in frontend environment variables or bundles.

## 6. Data retention and deletion

This policy is not finalized. Before implementation, decide:
- whether users can delete individual prediction records;
- whether account deletion cascades to prediction history;
- whether limited audit records must be retained after account deletion;
- how long prediction inputs and explanations are retained;
- whether users can export their data;
- whether any real personal/financial data is permitted in the portfolio demo.

Prefer synthetic/test data during development. Do not use real applicant data without an appropriate lawful basis, permissions, and safeguards.

## 7. Migrations and environment separation

- Keep migration files in version control.
- Apply schema changes through migrations, not manual production-only edits.
- Maintain separate development/test/production configuration.
- Use least-privilege database credentials where practical.
- Test migrations against a disposable/test database before production use.
- Document backup/recovery expectations according to the selected Supabase plan.

## 8. Open decisions

- UUID vs another primary-key strategy.
- Direct password management vs external authentication/session approach.
- Final schema/migration library.
- Typed columns vs JSON for model inputs and explanations.
- Prediction idempotency strategy.
- Account deletion, retention, export, and audit policy.
- Whether Supabase RLS is part of the final defense-in-depth design.
- Final database connectivity mode and connection-pooling requirements for Render.
