import json
from datetime import datetime
from uuid import UUID

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    computed_field,
    field_serializer,
)

from src.core.constants import PAGE_SIZE


class AuditDataLogBase(BaseModel):
    id: int
    entity_type: str
    action: str
    old_data: str | None = None
    new_data: str | None = None
    at: datetime

    class Config:
        from_attributes = True


class AuditDataLogSchema(AuditDataLogBase):
    @field_serializer("at", when_used="json")
    def serialize_at(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y %H:%M:%S")

    @field_serializer("old_data", when_used="json", mode="plain")
    def serialize_old_data(value: str | None) -> dict | None:
        if value is None:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}

    @field_serializer("new_data", when_used="json", mode="plain")
    def serialize_new_data(value: str | None) -> dict | None:
        if value is None:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}


class AuditActionLogBase(BaseModel):
    id: UUID
    user_id: int | None = None
    endpoint_name: str
    ip: str | None = None
    action: str
    path_params: str | None = None
    query_params: str | None = None
    request_data: str | None = None
    response_data: str | None = None
    status_code: int
    at: datetime

    class Config:
        from_attributes = True


class AuditActionLogSchema(AuditActionLogBase):
    audit_data_logs: list[AuditDataLogSchema] = []

    @field_serializer("at", when_used="json")
    def serialize_at(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y %H:%M:%S")

    @field_serializer("path_params", when_used="json", mode="plain")
    def serialize_path_params(value: str | None) -> dict | None:
        if value is None:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}

    @field_serializer("response_data", when_used="json", mode="plain")
    def serialize_response_data(value: str | None) -> dict | None:
        if value is None:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}

    @field_serializer("request_data", when_used="json", mode="plain")
    def serialize_request_data(value: str | None) -> dict | None:
        if value is None:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}

    @field_serializer("query_params", when_used="json", mode="plain")
    def serialize_query_params(value: str | None) -> dict | None:
        if value is None:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}


class AuditActionLogListSchema(BaseModel):
    audit_action_logs: list[AuditActionLogSchema]


class AuditActionLogFilterParams(BaseModel):
    page: int | None = Field(default=1, ge=1)

    @computed_field
    def limit(self) -> int:
        return PAGE_SIZE

    @computed_field
    def offset(self) -> int:
        return (self.page - 1) * PAGE_SIZE
