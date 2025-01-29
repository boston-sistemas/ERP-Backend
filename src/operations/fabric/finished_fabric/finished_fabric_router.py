from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db

from .finished_fabric_service import FinishedFabricService

router = APIRouter()


@router.get("/{fabric_id}")
async def read_finished_fabric(
    fabric_id: str,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FinishedFabricService(db=db, promec_db=promec_db)
    result = await service.read_fabric(fabric_id=fabric_id)

    if result.is_success:
        return result.value

    raise result.error


@router.get("/")
async def read_finished_fabrics(
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FinishedFabricService(db=db, promec_db=promec_db)
    result = await service.read_finished_fabrics()

    if result.is_success:
        return result.value

    raise result.error


@router.post("/")
async def create_finished_fabric(
    form: dict,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FinishedFabricService(db=db, promec_db=promec_db)
    result = await service.create_finished_fabric(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch("/{fabric_id}")
async def update_finished_fabric(
    fabric_id: str,
    form: dict,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FinishedFabricService(db=db, promec_db=promec_db)
    result = await service.update_finished_fabric(fabric_id=fabric_id, form=form)

    if result.is_success:
        return result.value

    raise result.error
