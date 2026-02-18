from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.web.context import template_context, templates

router = APIRouter(tags=["pages"])


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "about.html",
        template_context(request, app_name=settings.app_name),
    )
