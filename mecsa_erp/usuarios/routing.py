from fastapi import APIRouter

from mecsa_erp.usuarios.api import acceso, auth, rol, usuario

usuarios_router = APIRouter(prefix="/security/v1")
usuarios_router.include_router(usuario.router)
usuarios_router.include_router(rol.router)
usuarios_router.include_router(acceso.router)
usuarios_router.include_router(auth.router)