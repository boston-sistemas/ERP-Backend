from fastapi import APIRouter

from mecsa_erp.area_operaciones.modulo0.routing import router as modulo0_router
from mecsa_erp.area_operaciones.modulo1.routing import router as modulo1_router
from mecsa_erp.area_operaciones.modulo2.routing import router as modulo2_router
from mecsa_erp.usuarios.routing import router as usuarios_router

api_router = APIRouter()

api_router.include_router(modulo0_router)
api_router.include_router(modulo1_router)
api_router.include_router(modulo2_router)
api_router.include_router(usuarios_router)