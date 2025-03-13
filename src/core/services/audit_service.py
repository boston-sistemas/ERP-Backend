import json
import uuid
from functools import wraps
from typing import TypeVar

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from src.core.database import Base, get_db
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.security.models import AuditActionLog, AuditDataLog

from ...security.services.token_service import TokenService
from ..repository import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class AuditService:
    _context = {}

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

                    id = uuid.uuid4()

                    AuditService._context["id"] = id
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
                        response_data = (
                            json.dumps(encoded, default=str) if encoded else ""
                        )

                    query_params = json.dumps(dict(request.query_params), default=str)

                    request_data = (
                        json.dumps(request_data, default=str) if request_data else ""
                    )

                    audit_action_log_repository = BaseRepository(
                        model=AuditActionLog, db=db
                    )

                    audit_action_log = AuditActionLog(
                        id=id,
                        endpoint_name=endpoint_name,
                        user_id=user_id,
                        action=action,
                        query_params=query_params,
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

    # @staticmethod
    # def audit_data_log():
    #     def decorator(func):
    #         @wraps(func)
    #         async def wrapper(*args, **kwargs):
    #             from src.core.services.audit_service import AuditService
    #             if "id" in AuditService._context:
    #                 print(AuditService._context["id"])
    #                 print("id exists")
    #
    #             response = await func(*args, **kwargs)
    #             return response
    #         return wrapper
    #
    #     return decorator

    @staticmethod
    async def audit_data_log(
        db: AsyncSession,
        instance: ModelType,
        values_before: dict,
        values_after: dict,
    ):
        table_name = instance.__tablename__

        action = ""

        # print(values_before)
        # print("---->", values_after)

        if values_before and values_after:
            action = "UPDATE"
        elif not values_before and values_after:
            action = "CREATE"
        elif values_before and not values_after:
            action = "DELETE"

        audit_data_log_repository = BaseRepository(model=AuditDataLog, db=db)
        audit_data_log = AuditDataLog(
            entity_type=table_name,
            action=action,
            old_data=json.dumps(values_before, default=str),
            new_data=json.dumps(values_after, default=str),
            at=calculate_time(tz=PERU_TIMEZONE),
            action_id=AuditService._context["id"],
        )

        try:
            await audit_data_log_repository.save(audit_data_log)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_current_values(db: AsyncSession, instance):
        model = instance.__class__
        primary_keys = inspect(model).primary_key

        column_to_attr = {
            attr.columns[0].name: attr.key for attr in model.__mapper__.column_attrs
        }

        filter = and_(
            *[
                getattr(model, column_to_attr[col.name])
                == getattr(instance, column_to_attr[col.name])
                for col in primary_keys
            ]
        )

        audit_action_log_repository = BaseRepository(model=model, db=db)
        value = await audit_action_log_repository.find(filter=filter)

        if value:
            return {
                column_name: getattr(value, attr_key)
                for column_name, attr_key in column_to_attr.items()
            }
        return {}
