from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.core.schemas import ItemStatusUpdateSchema
from src.core.services import AuditService, PermissionService
from src.operations.schemas import (
    MecsaColorCreateSchema,
    MecsaColorListSchema,
    MecsaColorSchema,
    MecsaColorUpdateSchema,
)
from src.operations.services import MecsaColorService

router = APIRouter()


@router.get(
    "/{color_id}", response_model=MecsaColorSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def read_mecsa_color(
    request: Request, color_id: str, promec_db: AsyncSession = Depends(get_promec_db)
):
    service = MecsaColorService(promec_db)

    result = await service.read_mecsa_color(color_id=color_id)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=MecsaColorListSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_mecsa_colors(
    request: Request,
    include_inactives: bool = Query(default=False, alias="includeInactives"),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = MecsaColorService(promec_db=promec_db)

    result = await service.read_mecsa_colors(
        include_inactives=include_inactives, exclude_legacy=True
    )
    if result.is_success:
        return MecsaColorListSchema(mecsa_colors=result.value)

    raise result.error


@router.post("/", status_code=status.HTTP_201_CREATED)
@AuditService.audit_action_log()
async def create_mecsa_color(
    request: Request,
    form: MecsaColorCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = MecsaColorService(promec_db=promec_db)

    creation_result = await service.create_mecsa_color(form=form)
    if creation_result.is_success:
        return {"message": "El color ha sido creado con éxito."}

    raise creation_result.error


@router.patch("/{color_id}", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_mecsa_color(
    request: Request,
    color_id: str,
    form: MecsaColorUpdateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = MecsaColorService(promec_db=promec_db)

    result = await service.update_mecsa_color(color_id=color_id, form=form)
    if result.is_success:
        return {"message": "El color ha sido actualizado con éxito."}

    raise result.error


@router.put("/{color_id}/status", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_mecsa_color_status(
    request: Request,
    color_id: str,
    form: ItemStatusUpdateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = MecsaColorService(promec_db=promec_db)
    is_active = form.is_active
    result = await service.update_status(color_id=color_id, is_active=is_active)

    if result.is_success:
        msg = f"El color ha sido {'' if is_active else 'des'}activado con éxito"
        return {"message": msg}

    raise result.error
