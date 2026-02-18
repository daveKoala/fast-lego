import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from app.api.contracts import classify_error_action
from app.api.health import router as health_router
from app.api.pages import router as pages_router
from app.config import settings
from app.db.Connection import create_db_and_tables, seed_catalog_items

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(health_router)
app.include_router(pages_router)


def _get_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return request_id

    incoming = request.headers.get("x-request-id")
    if incoming:
        request.state.request_id = incoming
        return incoming

    generated = str(uuid4())
    request.state.request_id = generated
    return generated


def _build_error_payload(request: Request, message: str, status_code: int) -> dict[str, str]:
    return {
        "message": message,
        "action": classify_error_action(status_code).value,
        "x-request-id": _get_request_id(request),
    }


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    _get_request_id(request)
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, _exc: RequestValidationError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    payload = _build_error_payload(request, "Validation failed. Please modify request.", status_code)
    response = JSONResponse(status_code=status_code, content=payload)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    status_code = exc.status_code
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    payload = _build_error_payload(request, message, status_code)
    response = JSONResponse(status_code=status_code, content=payload)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, _exc: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    payload = _build_error_payload(request, "Unexpected internal error.", status_code)
    response = JSONResponse(status_code=status_code, content=payload)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.on_event("startup")
def on_startup() -> None:
    try:
        create_db_and_tables()
        seed_catalog_items()
    except Exception as exc:  # pragma: no cover
        logger.warning("Database initialization skipped: %s", exc)
