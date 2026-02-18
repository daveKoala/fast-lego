from pathlib import Path

from sqlalchemy import or_
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.config import settings
from app.db.Connection import get_session
from app.db.models import CatalogItem, SearchLog
from app.schemas.search import SearchForm, SearchResponse, SearchResultItem

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _template_context(request: Request, **context: object) -> dict[str, object]:
    base_context: dict[str, object] = {
        "request": request,
        "request_id": getattr(request.state, "request_id", None),
    }
    base_context.update(context)
    return base_context


@router.get("/", response_class=HTMLResponse)
def welcome_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "welcome.html",
        _template_context(request, app_name=settings.app_name, environment=settings.app_env),
    )


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "about.html",
        _template_context(request, app_name=settings.app_name),
    )


@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "search.html",
        _template_context(request, response=None, error=None, query=""),
    )


@router.post("/search", response_class=HTMLResponse)
def search_submit(
    request: Request,
    query: str = Form(...),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    try:
        form = SearchForm(query=query.strip())
    except Exception:
        return templates.TemplateResponse(
            "search.html",
            _template_context(request, response=None, error="Please enter a valid search term.", query=query),
        )

    try:
        statement = (
            select(CatalogItem)
            .where(
                or_(
                    CatalogItem.name.ilike(f"%{form.query}%"),
                    CatalogItem.category.ilike(f"%{form.query}%"),
                    CatalogItem.description.ilike(f"%{form.query}%"),
                )
            )
            .order_by(CatalogItem.name)
            .limit(10)
        )
        items = session.exec(statement).all()
    except Exception:
        return templates.TemplateResponse(
            "search.html",
            _template_context(
                request,
                response=None,
                error="Search is temporarily unavailable.",
                query=form.query,
            ),
        )

    response = SearchResponse(
        query=form.query,
        results=[
            SearchResultItem(name=item.name, category=item.category, description=item.description)
            for item in items
        ],
    )

    # Logging is best-effort and should not break search UX.
    try:
        session.add(SearchLog(query=form.query))
        session.commit()
    except Exception:
        session.rollback()

    return templates.TemplateResponse(
        "search.html",
        _template_context(request, response=response, error=None, query=form.query),
    )
