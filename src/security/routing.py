from fastapi import APIRouter

from security.routers import accesos, auth, roles, usuarios

router = APIRouter(prefix="/security/v1")  # tags=["Area Seguridad"]
router.include_router(auth.router)
router.include_router(usuarios.router)
router.include_router(roles.router)
router.include_router(accesos.router)
