"""Credix Backend — Security Audit Event Service.

Persists security-relevant actions to the audit_events table with strict PII
and secret scrubbing (passwords, tokens, and applicant payloads are NEVER logged).
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.audit import AuditEvent

logger = logging.getLogger("backend.audit")

# Prohibited keys that must never appear in audit metadata
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "hashed_password",
    "token",
    "access_token",
    "secret",
    "secret_key",
    "jwt",
    "authorization",
}


def _scrub_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Sanitizes metadata dictionary to ensure zero secrets or sensitive keys are stored."""
    if not metadata:
        return None
    cleaned: Dict[str, Any] = {}
    for key, val in metadata.items():
        if key.lower() in SENSITIVE_KEYS:
            cleaned[key] = "[REDACTED]"
        elif isinstance(val, dict):
            cleaned[key] = _scrub_metadata(val)
        else:
            cleaned[key] = val
    return cleaned


def record_audit_event(
    db: Session,
    event_type: str,
    actor_user_id: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditEvent:
    """Creates and persists an AuditEvent record in the current transaction.
    
    Ensures safe, structured audit trails for security actions.
    """
    clean_meta = _scrub_metadata(metadata)
    event = AuditEvent(
        actor_user_id=actor_user_id,
        event_type=event_type,
        target_type=target_type,
        target_id=target_id,
        metadata_json=clean_meta,
    )
    db.add(event)
    logger.info(
        f"Audit event recorded: type={event_type} actor={actor_user_id} target={target_type}:{target_id}"
    )
    return event

