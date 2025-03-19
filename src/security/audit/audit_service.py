import json
import uuid
from contextlib import asynccontextmanager
from functools import wraps
from typing import TypeVar

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.orm.properties import ColumnProperty

from src.core.database import Base, get_db
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.security.models import AuditActionLog, AuditDataLog

from ...core.repository import BaseRepository
from ...security.services.token_service import TokenService
from .audit_failures import AuditFailures
from .audit_repository import AuditRepository
from .audit_schema import (
    AuditActionLogFilterParams,
    AuditActionLogListSchema,
    AuditActionLogSchema,
)

ModelType = TypeVar("ModelType", bound=Base)


class AuditService:
    _context = {}

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit_action_log_repository = AuditRepository(db=db)
        self.audit_data_log_repository = BaseRepository(model=AuditDataLog, db=self.db)

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
    def audit_action_log(audit_save: bool = False):
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
                    path_params = json.dumps(request.path_params, default=str)
                    endpoint_name = getattr(request.scope.get("route"), "name", None)
                    user_agent = request.headers.get("user-agent", "Desconocido")
                    ip = request.client.host
                    action = request.method
                    query_params = json.dumps(dict(request.query_params), default=str)
                    request_data = (
                        json.dumps(request_data, default=str) if request_data else ""
                    )

                    AuditService._context["audit_save"] = audit_save
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
                        path_params=path_params,
                        query_params=query_params,
                        request_data=request_data,
                        response_data=response_data,
                        user_agent=user_agent,
                        status_code=status_code,
                        at=calculate_time(tz=PERU_TIMEZONE),
                        ip=ip,
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

        if (
            table_name == "audit_action_log" or table_name == "audit_data_log"
        ) and not AuditService._context["audit_save"]:
            return

        if values_before == values_after:
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
            AuditService._context["audit_save"] = False
            await audit_data_log_repository.save(audit_data_log)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_before_values(instance: ModelType):
        if (
            instance.__tablename__ == "audit_action_log"
            or instance.__tablename__ == "audit_data_log"
        ) and not AuditService._context["audit_save"]:
            return {}

        before_changes: dict = {}
        insp = inspect(instance)
        is_updated = False
        is_not_None = False
        for attr in instance.__mapper__.column_attrs:
            if not isinstance(attr, ColumnProperty) or attr.columns[0].name.startswith(
                "%"
            ):
                continue
            column_name = attr.columns[0].name
            if attr.key in insp.unloaded:
                before_changes[column_name] = None
            else:
                hist = get_history(instance, attr.key)
                if hist.has_changes():
                    old_value = hist.deleted
                    before_changes[column_name] = old_value[0] if old_value else None
                    is_updated |= bool(old_value[0]) if old_value else False
                else:
                    current_value = getattr(instance, attr.key)
                    before_changes[column_name] = current_value
                    is_not_None |= bool(current_value)

        if not is_updated and not is_not_None:
            return {}

        return before_changes

    @staticmethod
    async def get_after_values(instance: ModelType):
        if (
            instance.__tablename__ == "audit_action_log"
            or instance.__tablename__ == "audit_data_log"
        ) and not AuditService._context["audit_save"]:
            return {}

        after_changes: dict = {}
        insp = inspect(instance)
        for attr in instance.__mapper__.column_attrs:
            if not isinstance(attr, ColumnProperty) or attr.columns[0].name.startswith(
                "%"
            ):
                continue
            column_name = attr.columns[0].name
            if attr.key in insp.unloaded:
                after_changes[column_name] = None
            else:
                hist = get_history(instance, attr.key)
                if hist.has_changes():
                    new_value = hist.added
                    after_changes[column_name] = new_value[0] if new_value else None
                else:
                    current_value = getattr(instance, attr.key)
                    after_changes[column_name] = current_value

        return after_changes

    async def read_audit_action_log(
        self, audit_action_log_id: str
    ) -> Result[AuditActionLogSchema, CustomException]:
        audit_action_log_id = uuid.UUID(audit_action_log_id)
        audit_action_log: AuditActionLog = (
            await self.audit_action_log_repository.find_audit_action_log_by_id(
                audit_action_log_id=audit_action_log_id,
                include_action_data_logs=True,
            )
        )

        if not audit_action_log:
            return AuditFailures.AUDIT_ACTION_NOT_FOUND

        return Success(AuditActionLogSchema.model_validate(audit_action_log))

    async def read_audit_action_logs(
        self,
        filter_params: AuditActionLogFilterParams,
    ) -> Result[AuditActionLogListSchema, CustomException]:
        audit_action_logs = (
            await self.audit_action_log_repository.find_audit_action_logs(
                **filter_params.model_dump(exclude={"page"})
            )
        )

        return Success(AuditActionLogListSchema(audit_action_logs=audit_action_logs))
