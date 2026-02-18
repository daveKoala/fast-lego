from fastapi import APIRouter
from pydantic import BaseModel

from app.api.contracts import ApiEnvelope, build_envelope
from app.config import settings
from app.db.Connection import check_database_connection

router = APIRouter(tags=["health"])


class DatabaseStatus(BaseModel):
    connected: bool
    details: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: DatabaseStatus


@router.get("/health", response_model=ApiEnvelope, response_model_exclude_none=True)
def health() -> dict:
    connected, details = check_database_connection()
    status = "ok" if connected else "degraded"
    safe_details = details if connected or settings.debug else "Database connection failed"

    payload = HealthResponse(
        status=status,
        environment=settings.app_env,
        database=DatabaseStatus(connected=connected, details=safe_details),
    )
    return build_envelope(data=payload.dict())
