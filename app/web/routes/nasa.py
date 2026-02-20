from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.web.context import template_context, templates

import httpx


router = APIRouter(tags=["pages"])

@router.get("/nasa", response_class=HTMLResponse)
def nasa_page(request: Request) -> HTMLResponse:

    data = fetchImages()
    return templates.TemplateResponse(
        "nasa.html",
        template_context(request, app_name=settings.app_name, data=data),
    )

def fetchImages():
    # Placeholder for the actual implementation to fetch images from NASA API
    NASA_URL = "https://rovers.nebulum.one/api/v1/rovers/Perseverance/photos"
    params = {
        "earth_date": "2025-11-06",
        # "api_key": settings.nasa_api_key,
    }
    try:
        response = httpx.get(NASA_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch images: {response.status_code}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}