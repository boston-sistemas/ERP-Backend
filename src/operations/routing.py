from fastapi import APIRouter

from .routers import (
    movimiento_ingreso_crudo_router,
    programacion_tintoreria_router,
    reporte_stock_tejeduria_router,
    revision_stock_tejeduria_router,
)

router = APIRouter(prefix="/operations/v1")  # tags=["Area Operaciones"]
router.include_router(reporte_stock_tejeduria_router.router)
router.include_router(revision_stock_tejeduria_router.router)
router.include_router(programacion_tintoreria_router.router)
router.include_router(movimiento_ingreso_crudo_router.router)
