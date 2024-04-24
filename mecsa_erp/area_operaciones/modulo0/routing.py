from fastapi import APIRouter

from .api import orden_servicio_tejeduria, tejido

modulo0_router = APIRouter(prefix="/modulo0")

modulo0_router.include_router(orden_servicio_tejeduria.router)
modulo0_router.include_router(tejido.router)