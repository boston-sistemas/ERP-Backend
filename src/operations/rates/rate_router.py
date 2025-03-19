from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db

from .rate_schema import (
    RateCreateSchema,
    RateFilterParams,
    RateListSchema,
    RateSchema,
    RateUpdateSchema,
)
from .rate_service import RateService

router = APIRouter()


@router.get("/", response_model=RateListSchema)
async def read_service_rates(
    filter_params: RateFilterParams = Query(RateFilterParams()),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.read_service_rates(
        filter_params=filter_params,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/{rate_id}", response_model=RateSchema)
async def read_service_rate(
    rate_id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.read_service_rate(rate_id=rate_id)

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", response_model=RateSchema)
async def create_service_rate(
    form: RateCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.create_service_rate(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch("/{rate_id}", response_model=RateSchema)
async def update_service_rate(
    rate_id: str,
    form: RateUpdateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.update_service_rate(rate_id=rate_id, form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.get("/{rate_id}/is-updatable")
async def is_updated_permission_service_rate(
    rate_id: int,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.is_updated_permission_service_rate(rate_id=rate_id)

    if result.is_success:
        return {
            "updatable": True,
            "message": "La tarifa especificada puede ser actualizada.",
        }
    return {"updatable": False, "message": result.error.detail}
