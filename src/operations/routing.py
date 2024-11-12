from fastapi import APIRouter

from .routers import (
    mecsa_color_router,
    programacion_tintoreria_router,
    reporte_stock_tejeduria_router,
    revision_stock_tejeduria_router,
)

router = APIRouter(prefix="/operations/v1")  # tags=["Area Operaciones"]
router.include_router(reporte_stock_tejeduria_router.router)
router.include_router(revision_stock_tejeduria_router.router)
router.include_router(programacion_tintoreria_router.router)
router.include_router(mecsa_color_router.router)
