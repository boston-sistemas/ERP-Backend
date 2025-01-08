from fastapi import APIRouter

from .routers import (
    dyeing_service_dispatch_router,
    fabric_router,
    fiber_router,
    mecsa_color_router,
    orden_compra_router,
    programacion_tintoreria_router,
    reporte_stock_tejeduria_router,
    revision_stock_tejeduria_router,
    service_order_router,
    supplier_router,
    unit_router,
    weaving_service_entry_router,
    yarn_purchase_entry_router,
    yarn_router,
    yarn_weaving_dispatch_router,
)

router = APIRouter(prefix="/operations/v1")  # tags=["Area Operaciones"]
router.include_router(reporte_stock_tejeduria_router.router)
router.include_router(revision_stock_tejeduria_router.router)
router.include_router(programacion_tintoreria_router.router)
router.include_router(orden_compra_router.router)
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
    router=yarn_purchase_entry_router.router,
    prefix="/yarn-purchase-entries",
    tags=["[AREA OPERACIONES] GESTION DE INGRESO DE HILADOS POR O/C"],
)
router.include_router(
    router=yarn_weaving_dispatch_router.router,
    prefix="/yarn-weaving-dispatches",
    tags=["[AREA OPERACIONES] GESTION DE SALIDA DE HILADOS A TEJEDURIA"],
)
router.include_router(
    router=supplier_router.router,
    prefix="/suppliers",
    tags=["[AREA OPERACIONES] GESTION DE PROVEEDORES"],
)
router.include_router(
    router=service_order_router.router,
    prefix="/service-orders",
    tags=["[AREA OPERACIONES] GESTION DE ORDENES DE SERVICIO DE TEJEDURIA"],
)
router.include_router(
    router=weaving_service_entry_router.router,
    prefix="/weaving-service-entries",
    tags=["[AREA OPERACIONES] GESTION DE INGRESO POR SERVICIO DE TEJEDURIA"],
)
router.include_router(
    router=fabric_router.router,
    prefix="/fabrics",
    tags=["[AREA OPERACIONES] GESTION DE TEJIDOS"],
)
router.include_router(
    router=dyeing_service_dispatch_router.router,
    prefix="/dyeing-service-dispatches",
    tags=["[AREA OPERACIONES] GESTION DE SALIDA DE TINTORERIA"],
)
