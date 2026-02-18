from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def template_context(request: Request, **context: object) -> dict[str, object]:
    base_context: dict[str, object] = {
        "request": request,
        "request_id": getattr(request.state, "request_id", None),
    }
    base_context.update(context)
    return base_context
