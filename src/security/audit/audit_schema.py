from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditActionLogBase(BaseModel):
    id: UUID
    user_id: int
    endpoint_name: str
    action: str
    query_params: str
    request_data: str
    response_data: str
    status_code: int
    at: datetime

    class Config:
        from_attributes = True


class AuditActionLogSchema(AuditActionLogBase):
    pass
