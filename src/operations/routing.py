from fastapi import APIRouter

from .routers import programacion_tintoreria

router = APIRouter(prefix="/operations/v1")  # tags=["Area Operaciones"]
router.include_router(
    programacion_tintoreria.router, tags=["Area Operaciones - Programacion Tintoreria"]
)
