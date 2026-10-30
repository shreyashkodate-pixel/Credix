"""Credix Backend — FastAPI Application Entrypoint."""

import time
import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.router import api_router
from backend.app.api.v1.endpoints.health import health_check
from backend.app.core.database import get_db

# Configure backend logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend.main")

# Auto-create tables on startup if SQLite local development engine is active
if settings.DATABASE_URL.startswith("sqlite"):
    Base.metadata.create_all(bind=engine)
    logger.info("Initialized local development database schema.")


class SecurityAndCorrelationMiddleware(BaseHTTPMiddleware):
    """Injects trusted correlation Request IDs and essential security headers (Findings 1 & 4)."""

    async def dispatch(self, request: Request, call_next):
        # Always derive authoritative request ID from trusted server-side generation
        server_request_id = str(uuid.uuid4())
        request.state.request_id = server_request_id
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = (time.perf_counter() - start_time) * 1000

        # 1. Tracing & Performance correlation headers
        response.headers["X-Request-ID"] = server_request_id
        response.headers["X-Response-Time-Ms"] = f"{duration:.2f}"

        # 2. OWASP Recommended Security Headers (Finding 4)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS only when served over HTTPS in production
        if not settings.DEBUG and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


# FastAPI Application Factory
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Credix Loan Outcome Prediction Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# 1. Security and Request correlation ID middleware
app.add_middleware(SecurityAndCorrelationMiddleware)

# 2. CORS middleware (Frontend origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Standardized Error Envelopes (Finding 2, P-005, SRS FR-029)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Standardizes all HTTP exceptions into a unified error envelope."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    error_code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")

    if isinstance(exc.detail, dict):
        error_code = exc.detail.get("code", error_code)
        message = exc.detail.get("message", str(exc.detail))
    else:
        message = str(exc.detail) if exc.detail else "An error occurred."

    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
            },
            "request_id": request_id,
        },
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Standardizes request validation errors with field-level details."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({"field": field, "message": err["msg"]})

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid input fields.",
                "details": errors,
            },
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Standardizes unexpected internal exceptions without leaking stack traces or secrets."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception(f"Unhandled server error [request_id={request_id}]: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
            },
            "request_id": request_id,
        },
    )


# 4. Include Versioned API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# 5. Root Liveness Probe
@app.get("/health", tags=["health"])
def root_health():
    """Root liveness probe."""
    db = next(get_db())
    try:
        return health_check(db=db)
    finally:
        db.close()
