from fastapi import APIRouter

from .routers import (
    locations_router,
)

router = APIRouter(prefix="/resources/v1")
router.include_router(
    locations_router.router, tags=["Recursos - Ubicaciones"], prefix="/locations"
)
