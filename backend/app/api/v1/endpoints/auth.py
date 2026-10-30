"""Credix Backend — Authentication Endpoints."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User
from backend.app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from backend.app.services.audit_service import record_audit_event

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Creates a new applicant user account.
    
    Enforces FR-007: Role defaults strictly to 'user' to prevent self-provisioning of admin.
    Records AUTH_REGISTER audit event on success.
    """
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user = User(
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        role="user",
        is_active=True,
    )
    db.add(user)
    db.flush()

    record_audit_event(
        db=db,
        event_type="AUTH_REGISTER",
        actor_user_id=user.id,
        target_type="user",
        target_id=user.id,
        metadata={"email": user.email},
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    user_in: UserLogin,
    db: Session = Depends(get_db),
) -> Any:
    """Authenticates credentials and issues a signed JWT Bearer access token."""
    user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        # Record failed authentication attempt (zero passwords or credentials logged)
        record_audit_event(
            db=db,
            event_type="AUTH_LOGIN_FAILURE",
            actor_user_id=user.id if user else None,
            target_type="auth",
            target_id=user_in.email.lower(),
            metadata={"reason": "invalid_credentials"},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        record_audit_event(
            db=db,
            event_type="AUTH_LOGIN_FAILURE",
            actor_user_id=user.id,
            target_type="auth",
            target_id=user.email,
            metadata={"reason": "inactive_account"},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    record_audit_event(
        db=db,
        event_type="AUTH_LOGIN_SUCCESS",
        actor_user_id=user.id,
        target_type="user",
        target_id=user.id,
        metadata={"email": user.email},
    )
    db.commit()
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Returns profile information for the authenticated principal (FR-004)."""
    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Signals session termination for client-side token disposal."""
    return {"message": "Successfully logged out."}

