from fastapi import APIRouter

from operations.routing import router as operations_router
from resources.routing import router as resources_router
from security.routing import router as security_router

api_router = APIRouter()

api_router.include_router(operations_router)
api_router.include_router(security_router)
api_router.include_router(resources_router)
