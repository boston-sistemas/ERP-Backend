from copy import copy

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.schemas import ItemStatusUpdateSchema
from src.operations.docs import YarnRouterDocumentation
from src.operations.schemas import (
    YarnCreateSchema,
    YarnListSchema,
    YarnOptions,
    YarnSchema,
    YarnUpdateSchema,
)
from src.operations.services import YarnService

router = APIRouter()


@router.get("/{yarn_id}", response_model=YarnSchema)
async def read_yarn(
    yarn_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnService(db=db, promec_db=promec_db)
    result = await service.read_yarn(yarn_id=yarn_id, options=YarnOptions.all())

    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=YarnListSchema)
async def read_yarns(
    include_inactives: bool = Query(default=False, alias="includeInactives"),
    fiber_ids: list[str] = Query(default=None, alias="fiberIds", min_length=1),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnService(db=db, promec_db=promec_db)
    result = None
    options = YarnOptions.all()
    if fiber_ids:
        result = await service.read_yarns_by_recipe(
            fiber_ids=fiber_ids,
            options=options,
            include_inactives=include_inactives,
            exclude_legacy=True,
        )
        result.value.yarns.sort(key=lambda yarn: yarn.id)
    else:
        result = await service.read_yarns(
            options=options,
            include_inactives=include_inactives,
            exclude_legacy=True,
        )
    if result.is_success:
        return result.value

    raise result.error


@router.post("/", **YarnRouterDocumentation.create_yarn())
async def create_yarn(
    form: YarnCreateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnService(db=db, promec_db=promec_db)
    result = await service.create_yarn(form=form)

    if result.is_success:
        return {"message": "El hilado ha sido creado con éxito."}

    raise result.error


@router.patch("/{yarn_id}")
async def update_yarn(
    yarn_id: str,
    form: YarnUpdateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnService(db=db, promec_db=promec_db)
    result = await service.update_yarn(yarn_id=yarn_id, form=form)

    if result.is_success:
        return {"message": "El hilado ha sido actualizado con éxito."}

    error = copy(result.error)
    error.detail += " No se pudo actualizar el hilado."
    raise error


@router.put("/{yarn_id}/status")
async def update_yarn_status(
    yarn_id: str,
    form: ItemStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnService(db=db, promec_db=promec_db)
    is_active = form.is_active
    result = await service.update_status(yarn_id=yarn_id, is_active=is_active)

    if result.is_success:
        msg = f"El hilado ha sido {'' if is_active else 'des'}activado con éxito"
        return {"message": msg}

    raise result.error


@router.get(
    "/{yarn_id}/is-updatable", **YarnRouterDocumentation.check_is_yarn_updatable()
)
async def check_is_yarn_updatable(
    yarn_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnService(db=db, promec_db=promec_db)
    result = await service.validate_yarn_updatable(yarn_id=yarn_id)

    if result.is_success:
        return result.value

    raise result.error
