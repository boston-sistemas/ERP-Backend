from fastapi import APIRouter

from src.security.routers import acceso_router, auth, rol_router, user_router

router = APIRouter(prefix="/security/v1")  # tags=["Area Seguridad"]
router.include_router(auth.router)
router.include_router(user_router)
router.include_router(rol_router)
router.include_router(acceso_router)
