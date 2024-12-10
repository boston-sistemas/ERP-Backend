from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.operations.schemas import (
    MecsaColorCreateSchema,
    MecsaColorListSchema,
    MecsaColorSchema,
)
from src.operations.services import MecsaColorService

router = APIRouter()


@router.get("/{color_id}", response_model=MecsaColorSchema)
async def read_mecsa_color(
    color_id: str, promec_db: AsyncSession = Depends(get_promec_db)
):
    mecsa_color_service = MecsaColorService(promec_db)

    result = await mecsa_color_service.read_mecsa_color(color_id=color_id)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=MecsaColorListSchema)
async def read_mecsa_colors(promec_db: AsyncSession = Depends(get_promec_db)):
    mecsa_color_service = MecsaColorService(promec_db=promec_db)

    result = await mecsa_color_service.read_mecsa_colors(exclude_legacy=True)
    if result.is_success:
        return MecsaColorListSchema(mecsa_colors=result.value)

    raise result.error


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_mecsa_color(
    form: MecsaColorCreateSchema, promec_db: AsyncSession = Depends(get_promec_db)
):
    mecsa_color_service = MecsaColorService(promec_db=promec_db)

    creation_result = await mecsa_color_service.create_mecsa_color(form=form)
    if creation_result.is_success:
        return {"message": "El color ha sido creado con éxito."}

    raise creation_result.error
