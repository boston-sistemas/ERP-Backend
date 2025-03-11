import json
from functools import wraps

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.repository import BaseRepository
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.security.models import AuditActionLog

from ...security.services.token_service import TokenService


class AuditService:
    @staticmethod
    def audit_action_log():
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("request")
                if request is None:
                    for arg in args:
                        if isinstance(arg, Request):
                            request = arg
                            break
                async for db in get_db():
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
                    try:
                        request_data = await request.json()
                    except Exception:
                        request_data = None

                    response = await func(*args, **kwargs)

                    encoded = jsonable_encoder(response)
                    response_data: dict | None = None

                    if isinstance(response, BaseModel):
                        response_data = response.json()
                        route: APIRoute = request.scope.get("route")
                        status_code: int = route.status_code
                    elif isinstance(response, JSONResponse):
                        status_code: int = response.status_code
                        response_data = encoded.get("body")
                    else:
                        route: APIRoute = request.scope.get("route")
                        status_code: int = route.status_code
                        response_data = json.dumps(encoded) if encoded else ""

                    request_data = json.dumps(request_data) if request_data else ""

                    audit_action_log_repository = BaseRepository(
                        model=AuditActionLog, db=db
                    )

                    audit_action_log = AuditActionLog(
                        endpoint_name=endpoint_name,
                        user_id=user_id,
                        action=action,
                        request_data=request_data,
                        response_data=response_data,
                        status_code=status_code,
                        at=calculate_time(tz=PERU_TIMEZONE),
                    )

                    try:
                        await audit_action_log_repository.save(audit_action_log)
                    except Exception as e:
                        print(e)

                return response

            return wrapper

        return decorator
