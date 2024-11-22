from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.operations.schemas import (
    FiberCompleteListSchema,
    FiberCompleteSchema,
    FiberCreateSchema,
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
        return result.value

    raise result.error


@router.get("/", response_model=FiberCompleteListSchema)
async def read_fibers(
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.read_fibers()

    if result.is_success:
        return result.value


@router.post("/")
async def create_fiber(
    form: FiberCreateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = FiberService(db=db, promec_db=promec_db)
    result = await service.create_fiber(form=form)

    if result.is_success:
        return {"message": "Fibra creada con éxito."}

    raise result.error
