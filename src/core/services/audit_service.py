import json
from functools import wraps

from fastapi import Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.repository import BaseRepository
from src.security.models import AuditActionLog

from ...security.services.token_service import TokenService


class AuditService:
    @staticmethod
    def audit_action_log():
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("request")
                db: AsyncSession = kwargs.get("db")

                access_token = request.cookies.get("access_token")
                user_id: int | None = None
                endpoint_name = getattr(request.scope.get("route"), "name", None)
                action = request.method
                if access_token:
                    token_service = TokenService(db=db)

                    verification_result = token_service.verify_access_token(
                        token=access_token
                    )
                    if verification_result.is_failure:
                        user_id = None
                    else:
                        user_id = verification_result.value.user_id

                request_data: dict | None = None

                route: APIRoute = request.scope.get("route")
                status_code: int = route.status_code
                try:
                    request_data = await request.json()
                except Exception:
                    request_data = None

                response = await func(*args, **kwargs)

                response_data: dict | None = None

                encoded = jsonable_encoder(response)
                response_data = json.dumps(encoded)

                audit_action_log_repository = BaseRepository(
                    model=AuditActionLog, db=db
                )

                audit_action_log = AuditActionLog(
                    endpoint_name=endpoint_name,
                    user_id=user_id,
                    action=action,
                    request_data=json.dumps(request_data) if request_data else "",
                    response_data=json.dumps(response_data) if response_data else "",
                    status_code=status_code,
                )

                try:
                    await audit_action_log_repository.save(audit_action_log)
                except Exception as e:
                    print(e)

                return response

            return wrapper

        return decorator
