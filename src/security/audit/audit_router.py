from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.services import PermissionService

from .audit_schema import (
    AuditActionLogFilterParams,
    AuditActionLogListSchema,
    AuditActionLogSchema,
)
from .audit_service import AuditService

router = APIRouter()


@router.get(
    "/", response_model=AuditActionLogListSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log(True)
async def get_audit_action_logs(
    filter_params: AuditActionLogFilterParams = Query(AuditActionLogFilterParams()),
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db=db)
    result = await service.read_audit_action_logs(filter_params=filter_params)

    if result.is_success:
        return result.value
    raise result.error


@router.get(
    "/{audit_action_log_id}",
    response_model=AuditActionLogSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def get_audit_action_log(
    audit_action_log_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db=db)
    result = await service.read_audit_action_log(
        audit_action_log_id=audit_action_log_id
    )

    if result.is_success:
        return result.value
    raise result.error
