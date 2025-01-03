from fastapi import APIRouter

from .routers import (
    fabric_router,
    fiber_router,
    mecsa_color_router,
    programacion_tintoreria_router,
    reporte_stock_tejeduria_router,
    revision_stock_tejeduria_router,
    unit_router,
    yarn_router,
)

router = APIRouter(prefix="/operations/v1")  # tags=["Area Operaciones"]
router.include_router(reporte_stock_tejeduria_router.router)
router.include_router(revision_stock_tejeduria_router.router)
router.include_router(programacion_tintoreria_router.router)
router.include_router(
    mecsa_color_router.router,
    prefix="/mecsa-colors",
    tags=["[AREA OPERACIONES] GESTION DE COLORES MECSA"],
)
router.include_router(
    router=fiber_router.router,
    prefix="/fibers",
    tags=["[AREA OPERACIONES] GESTION DE FIBRAS"],
)
router.include_router(
    router=unit_router.router,
    prefix="/units",
    tags=["[AREA OPERACIONES] GESTION UNIDADES DE MEDIDA"],
)
router.include_router(
    router=yarn_router.router,
    prefix="/yarns",
    tags=["[AREA OPERACIONES] GESTION DE HILADOS"],
)
router.include_router(
    router=fabric_router.router,
    prefix="/fabrics",
    tags=["[AREA OPERACIONES] GESTION DE TEJIDOS"],
)
