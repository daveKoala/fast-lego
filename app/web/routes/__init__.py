from fastapi import APIRouter

from app.web.routes.about import router as about_router
from app.web.routes.search import router as search_router
from app.web.routes.welcome import router as welcome_router
from app.web.routes.nasa import router as nasa_router

router = APIRouter()
router.include_router(welcome_router)
router.include_router(about_router)
router.include_router(search_router)
router.include_router(nasa_router)
