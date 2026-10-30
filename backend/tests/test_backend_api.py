"""Credix Backend — End-to-End API Integration Tests.

Validates authentication, JWT authorization, Fair Lending demographic rejection,
atomic prediction persistence, ownership scoping, and admin role boundaries.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.models.prediction import PredictionRecord
from backend.app.models.audit import AuditEvent

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensures clean test database tables exist before and after running test suite."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_01_root_health_check():
    """Tests system health and liveness probes (FR-027)."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["ml_model_ready"] is True
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_02_auth_registration_and_login():
    """Tests user registration, duplicate prevention, and JWT token issuance."""
    email = "applicant_alice@example.com"
    password = "SuperSecretPassword123"

    # 1. Successful Registration
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == email
    assert user_data["role"] == "user"  # FR-007 enforced

    # 2. Duplicate Registration Rejection
    dup_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert dup_res.status_code == 400

    # 3. Invalid Login
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword123"},
    )
    assert bad_login.status_code == 401

    # 4. Successful Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 5. Access Protected /me Endpoint
    token = token_data["access_token"]
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email


def test_03_prediction_creation_and_atomic_persistence():
    """Tests prediction execution, TreeSHAP explanation, and PostgreSQL persistence."""
    # 1. Login user
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    token = login_res.json()["access_token"]

    # 2. Submit valid 9-feature loan application
    valid_payload = {
        "applicant_income": 6500.0,
        "coapplicant_income": 2000.0,
        "loan_amount": 130.0,
        "loan_amount_term": 360,
        "credit_history": 1,
        "education": "Graduate",
        "self_employed": "No",
        "dependents": "0",
        "property_area": "Semiurban",
    }

    pred_res = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json=valid_payload,
    )
    assert pred_res.status_code == 201
    pred_data = pred_res.json()
    assert pred_data["outcome"] in ["Approved", "Rejected"]
    assert "prediction_id" in pred_data
    assert pred_data["probability"] is not None
    assert pred_data["model_version"] == "1.0.0"
    assert pred_data["explanation"]["method"] == "TreeSHAP"
    assert len(pred_data["explanation"]["factors"]) > 0


def test_04_fair_lending_rejection():
    """Tests that prohibited demographic attributes (Gender, Married) are strictly rejected (D-023)."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    token = login_res.json()["access_token"]

    # Payload with prohibited 'gender'
    payload_with_gender = {
        "applicant_income": 6500.0,
        "coapplicant_income": 2000.0,
        "loan_amount": 130.0,
        "loan_amount_term": 360,
        "credit_history": 1,
        "education": "Graduate",
        "self_employed": "No",
        "dependents": "0",
        "property_area": "Semiurban",
        "gender": "Male",
    }

    res = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json=payload_with_gender,
    )
    assert res.status_code == 422
    err_body = res.json()
    assert "error" in err_body
    assert err_body["error"]["code"] == "VALIDATION_ERROR"
    assert any("Prohibited demographic" in d["message"] for d in err_body["error"]["details"])


def test_05_user_history_ownership_enforcement():
    """Enforces D-016 & FR-018: A user can NEVER view another user's prediction history."""
    # 1. Login Alice and create a prediction
    alice_login = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    alice_token = alice_login.json()["access_token"]

    alice_pred = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={
            "applicant_income": 5000.0,
            "coapplicant_income": 1000.0,
            "loan_amount": 100.0,
            "loan_amount_term": 360,
            "credit_history": 1,
            "education": "Graduate",
            "self_employed": "No",
            "dependents": "0",
            "property_area": "Urban",
        },
    ).json()
    alice_pred_id = alice_pred["prediction_id"]

    # 2. Register and Login Bob (second user)
    bob_email = "applicant_bob@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": bob_email, "password": "BobsPassword123"},
    )
    bob_login = client.post(
        "/api/v1/auth/login",
        json={"email": bob_email, "password": "BobsPassword123"},
    )
    bob_token = bob_login.json()["access_token"]

    # 3. Bob queries his own history -> MUST BE EMPTY
    bob_hist = client.get(
        "/api/v1/predictions/history",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert bob_hist.status_code == 200
    assert bob_hist.json()["total"] == 0
    assert len(bob_hist.json()["items"]) == 0

    # 4. Bob attempts to access Alice's prediction by ID -> MUST RETURN 404
    bob_probe = client.get(
        f"/api/v1/predictions/history/{alice_pred_id}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert bob_probe.status_code == 404


def test_06_admin_authorization_boundaries():
    """Enforces FR-005 & FR-024: Non-admin users are strictly denied administrative endpoints."""
    # 1. Regular user attempts to access admin dashboard -> MUST RETURN 403 FORBIDDEN
    alice_login = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    alice_token = alice_login.json()["access_token"]

    forbidden_res = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert forbidden_res.status_code == 403

    # 2. Provision Admin User in database
    db = SessionLocal()
    admin_user = db.query(User).filter(User.email == "admin@credix.io").first()
    if not admin_user:
        admin_user = User(
            email="admin@credix.io",
            hashed_password=get_password_hash("AdminMasterSecret2026"),
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
    db.close()

    # 3. Admin logs in
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@credix.io", "password": "AdminMasterSecret2026"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    # 4. Admin accesses dashboard -> 200 OK with aggregate metrics
    dashboard_res = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert dashboard_res.status_code == 200
    metrics = dashboard_res.json()
    assert metrics["total_users"] >= 2
    assert metrics["total_predictions"] >= 1
    assert "approval_rate_percent" in metrics


def test_07_request_id_persistence_matches_response_header():
    """Enforces Finding 1: Verifies stored PredictionRecord.request_id strictly matches the response X-Request-ID."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    token = login_res.json()["access_token"]

    pred_res = client.post(
        "/api/v1/predictions",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Request-ID": "client-spoofed-id-should-be-ignored",
        },
        json={
            "applicant_income": 6000.0,
            "coapplicant_income": 1500.0,
            "loan_amount": 120.0,
            "loan_amount_term": 360,
            "credit_history": 1,
            "education": "Graduate",
            "self_employed": "No",
            "dependents": "0",
            "property_area": "Urban",
        },
    )
    assert pred_res.status_code == 201
    pred_data = pred_res.json()
    prediction_id = pred_data["prediction_id"]
    response_request_id = pred_res.headers.get("X-Request-ID")
    assert response_request_id is not None
    # Verify server-generated ID was used, not the client spoofed ID
    assert response_request_id != "client-spoofed-id-should-be-ignored"

    # Query DB to check persisted record
    db = SessionLocal()
    record = db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()
    assert record is not None
    assert record.request_id == response_request_id
    db.close()


def test_08_standardized_error_envelopes():
    """Enforces Finding 2 & P-005: Verifies consistent error envelope on 400, 401, 403, 404, 422."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    token = login_res.json()["access_token"]

    # 1. HTTP 400 (Duplicate Registration)
    res_400 = client.post(
        "/api/v1/auth/register",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    assert res_400.status_code == 400
    body_400 = res_400.json()
    assert "error" in body_400
    assert body_400["error"]["code"] == "BAD_REQUEST"
    assert "already exists" in body_400["error"]["message"]
    assert "request_id" in body_400

    # 2. HTTP 401 (Invalid Credentials)
    res_401 = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "WrongPassword!"},
    )
    assert res_401.status_code == 401
    body_401 = res_401.json()
    assert "error" in body_401
    assert body_401["error"]["code"] == "UNAUTHORIZED"
    assert "request_id" in body_401

    # 3. HTTP 403 (Non-admin hitting admin endpoint)
    res_403 = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_403.status_code == 403
    body_403 = res_403.json()
    assert "error" in body_403
    assert body_403["error"]["code"] == "FORBIDDEN"
    assert "request_id" in body_403

    # 4. HTTP 404 (Non-existent prediction ID)
    res_404 = client.get(
        "/api/v1/predictions/history/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_404.status_code == 404
    body_404 = res_404.json()
    assert "error" in body_404
    assert body_404["error"]["code"] == "NOT_FOUND"
    assert "request_id" in body_404

    # 5. HTTP 422 (Validation Error)
    res_422 = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json={"applicant_income": -100.0},
    )
    assert res_422.status_code == 422
    body_422 = res_422.json()
    assert "error" in body_422
    assert body_422["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in body_422["error"]
    assert "request_id" in body_422


def test_09_audit_event_persistence_and_sensitive_data_exclusion():
    """Enforces Finding 3: Verifies AuditEvent persistence and strict secret scrubbing."""
    db = SessionLocal()
    events = db.query(AuditEvent).all()
    assert len(events) >= 3

    event_types = [e.event_type for e in events]
    assert "AUTH_REGISTER" in event_types
    assert "AUTH_LOGIN_SUCCESS" in event_types
    assert "AUTH_LOGIN_FAILURE" in event_types
    assert "ADMIN_DASHBOARD_ACCESS" in event_types

    # Strict sensitive data scrubbing check
    forbidden_keys = {"password", "hashed_password", "token", "access_token", "secret"}
    for e in events:
        meta = e.metadata_json or {}
        for key, val in meta.items():
            assert key.lower() not in forbidden_keys, f"Forbidden key '{key}' found in audit metadata!"
            if isinstance(val, str):
                assert "SuperSecretPassword123" not in val
                assert "AdminMasterSecret2026" not in val
                assert "Bearer" not in val
    db.close()


def test_10_security_response_headers():
    """Enforces Finding 4: Verifies OWASP security response headers across endpoints."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


def test_11_jwt_security_negative_cases():
    """Verifies expired, tampered, and missing JWT token handling."""
    from datetime import datetime, timedelta, timezone
    import jwt
    from backend.app.core.config import settings

    # 1. Expired Token
    expired_payload = {
        "sub": "some-user-id",
        "role": "user",
        "exp": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    res_exp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res_exp.status_code == 401
    assert res_exp.json()["error"]["code"] == "UNAUTHORIZED"

    # 2. Tampered Token
    res_tampered = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}tampered"})
    assert res_tampered.status_code == 401
    assert res_tampered.json()["error"]["code"] == "UNAUTHORIZED"

    # 3. Missing Auth Header
    res_missing = client.get("/api/v1/auth/me")
    assert res_missing.status_code == 401
    assert res_missing.json()["error"]["code"] == "UNAUTHORIZED"


def test_12_malformed_inputs_and_inference_rollback():
    """Verifies malformed prediction bounds and atomic database rollback on inference crash."""
    from unittest.mock import patch
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant_alice@example.com", "password": "SuperSecretPassword123"},
    )
    token = login_res.json()["access_token"]

    # 1. Invalid loan amount term (not in allowed list)
    bad_term_payload = {
        "applicant_income": 5000.0,
        "coapplicant_income": 0.0,
        "loan_amount": 100.0,
        "loan_amount_term": 999,
        "credit_history": 1,
        "education": "Graduate",
        "self_employed": "No",
        "dependents": "0",
        "property_area": "Urban",
    }
    res_bad_term = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json=bad_term_payload,
    )
    assert res_bad_term.status_code == 422
    assert res_bad_term.json()["error"]["code"] == "VALIDATION_ERROR"

    # 2. Invalid credit history (not 0 or 1)
    bad_credit_payload = bad_term_payload.copy()
    bad_credit_payload["loan_amount_term"] = 360
    bad_credit_payload["credit_history"] = 5
    res_bad_credit = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json=bad_credit_payload,
    )
    assert res_bad_credit.status_code == 422
    assert res_bad_credit.json()["error"]["code"] == "VALIDATION_ERROR"

    # 3. Simulated inference engine crash -> must return 500 and rollback DB
    valid_payload = bad_term_payload.copy()
    valid_payload["loan_amount_term"] = 360
    valid_payload["credit_history"] = 1

    db = SessionLocal()
    alice = db.query(User).filter(User.email == "applicant_alice@example.com").first()
    count_before = db.query(PredictionRecord).filter(PredictionRecord.user_id == alice.id).count()

    with patch("ml.inference.services.prediction_service.PredictionService.predict", side_effect=RuntimeError("Simulated TreeSHAP C crash")):
        res_crash = client.post(
            "/api/v1/predictions",
            headers={"Authorization": f"Bearer {token}"},
            json=valid_payload,
        )
        assert res_crash.status_code == 500
        assert res_crash.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"

    count_after = db.query(PredictionRecord).filter(PredictionRecord.user_id == alice.id).count()
    assert count_after == count_before, "Rollback failed: record was created despite inference failure!"
    db.close()

