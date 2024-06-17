from fastapi import APIRouter

from .routers import programacion_tintoreria, stock

router = APIRouter(prefix="/operations/v1")  # tags=["Area Operaciones"]
router.include_router(stock.router, tags=["Area Operaciones - Stock"])
router.include_router(
    programacion_tintoreria.router, tags=["Area Operaciones - Programacion Tintoreria"]
)
