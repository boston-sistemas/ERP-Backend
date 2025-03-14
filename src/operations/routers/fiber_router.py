from copy import copy

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.schemas import ItemStatusUpdateSchema
from src.core.services import PermissionService
from src.operations.docs import FiberRouterDocumentation
from src.operations.schemas import (
    FiberCreateSchema,
    FiberExtendedListSchema,
    FiberExtendedSchema,
    FiberOptions,
    FiberUpdateSchema,
)
from src.operations.services import FiberService
from src.security.audit import AuditService

router = APIRouter()


@router.get(
    "/{fiber_id}",
    responses={200: {"model": FiberExtendedSchema}},
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_fiber(
    request: Request,
    fiber_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.read_fiber(fiber_id=fiber_id, options=FiberOptions.all())

    if result.is_success:
        fiber = result.value
        update_check_mapping = (
            await service.validate_fibers_updatable(fibers=[fiber])
        ).value

        return FiberExtendedSchema.model_validate(result.value).model_copy(
            update={"update_check": update_check_mapping[fiber.id]}
        )

    raise result.error


@router.get(
    "/",
    responses={200: {"model": FiberExtendedListSchema}},
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_fibers(
    request: Request,
    include_inactives: bool = Query(default=False, alias="includeInactives"),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.read_fibers(
        include_inactives=include_inactives, options=FiberOptions.all()
    )

    if result.is_success:
        fibers = result.value
        update_check_mapping = (
            await service.validate_fibers_updatable(fibers=fibers)
        ).value

        return FiberExtendedListSchema(
            fibers=[
                FiberExtendedSchema.model_validate(fiber).model_copy(
                    update={"update_check": update_check_mapping[fiber.id]}
                )
                for fiber in fibers
            ]
        )


@router.post("/", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def create_fiber(
    request: Request,
    form: FiberCreateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.create_fiber(form=form)

    if result.is_success:
        return {"message": "La fibra ha sido creada con éxito."}

    error = copy(result.error)
    error.detail += " No se pudo crear la fibra."
    raise error


@router.patch("/{fiber_id}", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_fiber(
    request: Request,
    fiber_id: str,
    form: FiberUpdateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.update_fiber(fiber_id=fiber_id, form=form)

    if result.is_success:
        return {"message": "La fibra ha sido actualizada con éxito."}

    error = copy(result.error)
    error.detail += " No se pudo actualizar la fibra."
    raise error


@router.put("/{fiber_id}/status", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_fiber_status(
    request: Request,
    fiber_id: str,
    form: ItemStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    is_active = form.is_active
    result = await service.update_status(fiber_id=fiber_id, is_active=is_active)

    if result.is_success:
        msg = f"La fibra ha sido {'' if is_active else 'des'}activada con éxito"
        return {"message": msg}

    raise result.error


@router.get(
    "/{fiber_id}/is-updatable",
    **FiberRouterDocumentation.check_is_fiber_updatable(),
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def check_is_fiber_updatable(
    request: Request,
    fiber_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.validate_fiber_updatable(fiber_id=fiber_id)

    if result.is_success:
        return result.value

    raise result.error
