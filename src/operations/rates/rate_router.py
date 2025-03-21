from fastapi import APIRouter, Depends, Query, Request, status
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
from .rates_router_doc import RateRouterDocumentation

router = APIRouter()


@router.get(
    "/", **RateRouterDocumentation.read_service_rates(), status_code=status.HTTP_200_OK
)
async def read_service_rates(
    request: Request,
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


@router.get(
    "/{rate_id}",
    **RateRouterDocumentation.read_service_rate(),
    status_code=status.HTTP_200_OK,
)
async def read_service_rate(
    request: Request,
    rate_id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.read_service_rate(rate_id=rate_id)

    if result.is_success:
        return result.value

    raise result.error


@router.post(
    "/",
    **RateRouterDocumentation.create_service_rate(),
    status_code=status.HTTP_201_CREATED,
)
async def create_service_rate(
    request: Request,
    form: RateCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.create_service_rate(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch(
    "/{rate_id}",
    **RateRouterDocumentation.update_service_rate(),
    status_code=status.HTTP_200_OK,
)
async def update_service_rate(
    request: Request,
    rate_id: str,
    form: RateUpdateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = RateService(promec_db=promec_db)
    result = await service.update_service_rate(rate_id=rate_id, form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{rate_id}/is-updatable",
    **RateRouterDocumentation.is_updated_permission_service_rate(),
    status_code=status.HTTP_200_OK,
)
async def is_updated_permission_service_rate(
    request: Request,
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
