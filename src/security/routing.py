from fastapi import APIRouter

from src.security.routers import (
    acceso_router,
    auth_router,
    parameter_category_router,
    parameter_public_router,
    parameter_router,
    rol_router,
    user_router,
)

router = APIRouter(prefix="/security/v1")
router.include_router(auth_router.router)
router.include_router(user_router.router)
router.include_router(rol_router.router)
router.include_router(acceso_router.router)
router.include_router(
    parameter_category_router.router,
    prefix="/parameter-categories",
    tags=["[SISTEMA] CATEGORÍA DE PARÁMETROS"],
)
router.include_router(
    parameter_router.router,
    prefix="/parameters",
    tags=["[SISTEMA] PARÁMETROS"],
)
router.include_router(
    parameter_public_router.router,
    prefix="/parameters/public",
    tags=["[SISTEMA] PARÁMETROS PÚBLICOS"],
)
