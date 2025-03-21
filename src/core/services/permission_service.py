from functools import wraps

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.failures import AuthFailures

from ...security.services.auth_service import AuthService
from ...security.services.token_service import TokenService


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def check_permission(access: int, operation: int):
        def decorator(func):
            @wraps(func)
            async def wrapper(
                request: Request, db: AsyncSession = Depends(get_db), *args, **kwargs
            ):
                access_token = request.cookies.get("access_token")
                token_service = TokenService(db=db)
                auth_service = AuthService(db=db)

                verification_result = token_service.verify_access_token(
                    token=access_token
                )
                if verification_result.is_failure:
                    raise verification_result.error

                token_data = token_service.decode_token(token=access_token)

                auth_result = await auth_service.is_valid_access_operation_to_user(
                    user_id=token_data["sub"],
                    access_id=access,
                    operation_id=operation,
                )

                if not auth_result:
                    raise AuthFailures.UNAUTHORIZED_FAILURE.error

                return await func(request, db, *args, **kwargs)

            return wrapper

        return decorator
