import json
import uuid
from contextlib import asynccontextmanager
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

from ...core.repository import BaseRepository
from ...security.services.token_service import TokenService

ModelType = TypeVar("ModelType", bound=Base)


class AuditService:
    _context = {}

    @staticmethod
    @asynccontextmanager
    async def get_db_session():
        async for db in get_db():
            yield db

    @staticmethod
    async def get_request_data(request: Request):
        try:
            return await request.json()
        except Exception:
            return None

    @staticmethod
    def get_user_id_from_token(db, request):
        access_token = request.cookies.get("access_token")
        if not access_token:
            return None

        token_service = TokenService(db=db)
        verification_result = token_service.verify_access_token(token=access_token)
        return (
            verification_result.value.user_id
            if verification_result.is_success
            else None
        )

    @staticmethod
    def extract_response_data(response, request):
        encoded = jsonable_encoder(response)
        route = request.scope.get("route")

        if isinstance(response, BaseModel):
            return response.json(), route.status_code
        if isinstance(response, JSONResponse):
            return encoded.get("body"), response.status_code
        return json.dumps(encoded, default=str) if encoded else "", route.status_code

    @staticmethod
    def audit_action_log():
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("request") or next(
                    (arg for arg in args if isinstance(arg, Request)), None
                )
                if not request:
                    return await func(*args, **kwargs)

                async with AuditService.get_db_session() as db:
                    user_id = AuditService.get_user_id_from_token(db, request)
                    request_data = await AuditService.get_request_data(request)
                    endpoint_name = getattr(request.scope.get("route"), "name", None)
                    action = request.method
                    query_params = json.dumps(dict(request.query_params), default=str)
                    request_data = (
                        json.dumps(request_data, default=str) if request_data else ""
                    )

                    AuditService._context["id"] = audit_id = uuid.uuid4()
                    response = await func(*args, **kwargs)

                    response_data, status_code = AuditService.extract_response_data(
                        response, request
                    )

                    audit_entry = AuditActionLog(
                        id=audit_id,
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
                        await BaseRepository(model=AuditActionLog, db=db).save(
                            audit_entry
                        )
                    except Exception as e:
                        print(e)

                return response

            return wrapper

        return decorator

    @staticmethod
    async def audit_data_log(
        db: AsyncSession,
        instance: ModelType,
        values_before: dict,
        values_after: dict,
    ):
        table_name = instance.__tablename__

        if table_name == "audit_action_log" or table_name == "audit_data_log":
            return

        action = ""

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
    async def get_current_values(db: AsyncSession, instance: ModelType):
        if (
            instance.__tablename__ == "audit_action_log"
            or instance.__tablename__ == "audit_data_log"
        ):
            return {}

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
