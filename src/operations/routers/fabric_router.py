from copy import copy

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.operations.schemas import (
    FabricCreateSchema,
    FabricListSchema,
    FabricSchema,
    FabricUpdateSchema,
)
from src.operations.services import FabricService

router = APIRouter()


@router.get("/{fabric_id}", response_model=FabricSchema)
async def read_fabric(
    fabric_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FabricService(db=db, promec_db=promec_db)
    result = await service.read_fabric(
        fabric_id=fabric_id,
        include_fabric_type=True,
        include_color=True,
        include_recipe=True,
        include_yarn_instance_to_recipe=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=FabricListSchema)
async def read_fabrics(
    include_inactives: bool = Query(default=False),
    yarn_ids: list[str] = Query(default=None, min_length=1),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FabricService(db=db, promec_db=promec_db)
    result = None
    if yarn_ids:
        result = await service.find_fabrics_by_recipe(
            yarn_ids=yarn_ids,
            include_fabric_type=True,
            include_color=True,
            include_recipe=True,
            include_yarn_instance_to_recipe=True,
            exclude_legacy=True,
        )
        result.value.fabrics.sort(key=lambda fabric: fabric.id)
    else:
        result = await service.read_fabrics(
            include_inactives=include_inactives,
            include_fabric_type=True,
            include_color=True,
            include_recipe=True,
            include_yarn_instance_to_recipe=True,
            exclude_legacy=True,
        )
    if result.is_success:
        return result.value

    raise result.error


@router.post("/")
async def create_fabric(
    form: FabricCreateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FabricService(db=db, promec_db=promec_db)
    result = await service.create_fabric(form=form)

    if result.is_success:
        return {"message": "El tejido ha sido creado con éxito."}

    raise result.error


@router.patch("/{fabric_id}")
async def update_fabric(
    fabric_id: str,
    form: FabricUpdateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FabricService(db=db, promec_db=promec_db)
    result = await service.update_fabric(fabric_id=fabric_id, form=form)

    if result.is_success:
        return {"message": "El tejido ha sido actualizado con éxito."}

    error = copy(result.error)
    error.detail += " No se pudo actualizar el tejido."
    raise error


@router.put("/{fabric_id}/status")
async def update_fabric_status(
    fabric_id: str,
    is_active: bool = Body(embed=True),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FabricService(db=db, promec_db=promec_db)
    result = await service.update_status(fabric_id=fabric_id, is_active=is_active)

    if result.is_success:
        msg = f"El tejido ha sido {'' if is_active else 'des'}activado con éxito"
        return {"message": msg}

    raise result.error
