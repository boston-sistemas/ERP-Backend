from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.services import AuditService, PermissionService
from src.security.audit import AccesoService
from src.security.schemas import (
    AccesoListSchema,
    AccesoSchema,
    AccessCreateSchema,
    AccessUpdateSchema,
)

router = APIRouter(tags=["Seguridad - Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema, status_code=status.HTTP_200_OK)
# @PermissionService.check_permission(1, 101)
@AuditService.audit_action_log()
async def read_accesos(
    request: Request, db: AsyncSession = Depends(get_db)
) -> AccesoListSchema:
    acceso_service = AccesoService(db)

    accesos = await acceso_service.read_accesos()

    if accesos.is_success:
        return accesos.value

    raise accesos.error


@router.get("/{acceso_id}", response_model=AccesoSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_acceso(
    request: Request, acceso_id: int, db: AsyncSession = Depends(get_db)
):
    acceso_service = AccesoService(db)

    result = await acceso_service.read_acceso(
        acceso_id=acceso_id, include_operations=True
    )

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", response_model=AccesoSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def create_access(
    request: Request, form: AccessCreateSchema, db: AsyncSession = Depends(get_db)
):
    access_service = AccesoService(db)

    result = await access_service.create_access(form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch(
    "/{access_id}", response_model=AccesoSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def update_access(
    request: Request,
    access_id: int,
    form: AccessUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    access_service = AccesoService(db)

    result = await access_service.update_access(form=form, access_id=access_id)

    if result.is_success:
        return result.value

    raise result.error
