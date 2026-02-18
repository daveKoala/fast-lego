from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class ApiEnvelope(BaseModel):
    data: Any
    continuationToken: str | None = None
    next: str | None = None
    message: str | None = None


class ErrorAction(str, Enum):
    RETRY = "retry"
    MODIFY_REQUEST = "modify_request"
    NOT_AUTH = "not_auth"
    INTERNAL_ERROR = "internal_error"


def build_envelope(
    data: Any,
    message: str | None = None,
    continuation_token: str | None = None,
    next_link: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"data": data}
    if continuation_token is not None:
        payload["continuationToken"] = continuation_token
    if next_link is not None:
        payload["next"] = next_link
    if message is not None:
        payload["message"] = message
    return payload


def classify_error_action(status_code: int) -> ErrorAction:
    if status_code in {401, 403}:
        return ErrorAction.NOT_AUTH
    if status_code in {408, 425, 429, 502, 503, 504}:
        return ErrorAction.RETRY
    if 400 <= status_code < 500:
        return ErrorAction.MODIFY_REQUEST
    return ErrorAction.INTERNAL_ERROR
