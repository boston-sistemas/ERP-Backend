from copy import copy

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.operations.schemas import (
    FiberCompleteListSchema,
    FiberCompleteSchema,
    FiberCreateSchema,
    FiberUpdateSchema,
)
from src.operations.services import FiberService

router = APIRouter()


@router.get("/{fiber_id}", response_model=FiberCompleteSchema)
async def read_fiber(
    fiber_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.read_fiber(
        fiber_id=fiber_id, include_category=True, include_color=True
    )

    if result.is_success:
        return FiberCompleteSchema.model_validate(result.value)

    raise result.error


@router.get("/", response_model=FiberCompleteListSchema)
async def read_fibers(
    include_inactives: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.read_fibers(
        include_inactives=include_inactives, include_category=True, include_color=True
    )

    if result.is_success:
        return FiberCompleteListSchema(fibers=result.value)


@router.post("/")
async def create_fiber(
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


@router.patch("/{fiber_id}")
async def update_fiber(
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


@router.put("/{fiber_id}/status")
async def update_fiber_status(
    fiber_id: str,
    is_active: bool = Body(embed=True),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.update_status(fiber_id=fiber_id, is_active=is_active)

    if result.is_success:
        msg = f"La fibra ha sido {''if is_active else 'des'}activada con éxito"
        return {"message": msg}

    raise result.error
