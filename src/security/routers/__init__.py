from .acceso import router as acceso_router
from .rol import router as rol_router
from .user import router as user_router

__all__ = ["user_router", "rol_router", "acceso_router"]
