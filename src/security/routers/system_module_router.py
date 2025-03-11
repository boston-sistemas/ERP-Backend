from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.services import AuditService, PermissionService
from src.security.schemas import (
    SystemModuleCreateSchema,
    SystemModuleFilterParams,
    SystemModuleListSchema,
    SystemModuleSchema,
)
from src.security.services import SystemModuleService

router = APIRouter()


@router.get("/", response_model=SystemModuleListSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_system_modules(
    request: Request,
    filter_params: SystemModuleFilterParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = SystemModuleService(db=db)
    result = await service.read_system_modules(filter_params=filter_params)

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{system_module_id}",
    response_model=SystemModuleSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_system_module(
    request: Request,
    system_module_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = SystemModuleService(db=db)
    result = await service.read_system_module(system_module_id=system_module_id)

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", response_model=SystemModuleSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def create_system_module(
    request: Request,
    form: SystemModuleCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    service = SystemModuleService(db=db)
    result = await service.create_system_module(form=form)

    if result.is_success:
        return result.value

    raise result.error
