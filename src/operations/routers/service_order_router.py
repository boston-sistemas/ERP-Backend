from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.operations.schemas import (
    ServiceOrderCreateSchema,
    ServiceOrderFilterParams,
    ServiceOrderListSchema,
    ServiceOrderSchema,
    ServiceOrderUpdateSchema,
)
from src.operations.services import ServiceOrderService

router = APIRouter()


@router.get("/", response_model=ServiceOrderListSchema)
async def read_service_orders(
    filter_params: ServiceOrderFilterParams = Query(ServiceOrderFilterParams()),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.read_service_orders(
        order_type="TJ",
        filter_params=filter_params,
        include_status=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/{order_id}", response_model=ServiceOrderSchema)
async def read_service_order(
    order_id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.read_service_order(
        order_type="TJ",
        order_id=order_id,
        include_detail=True,
        include_status=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", response_model=ServiceOrderSchema)
async def create_weaving_service_order(
    form: ServiceOrderCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.create_weaving_service_order(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch("/{order_id}", response_model=ServiceOrderSchema)
async def update_weaving_service_order(
    order_id: str,
    form: ServiceOrderUpdateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.update_weaving_service_order(order_id=order_id, form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.put("/{order_id}/anulate")
async def anulate_weaving_service_order(
    order_id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.anulate_weaving_service_order(order_id=order_id)

    if result.is_success:
        return {
            "message": "La orden de servicio de tejeduría ha sido anulada correctamente."
        }

    raise result.error


@router.get("/{order_id}/is-updatable")
async def is_updated_permission_weaving_service_order(
    order_id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.is_updated_permission_weaving_service_order(
        order_id=order_id
    )

    if result.is_success:
        return {
            "updatable": True,
            "message": "La orden de servicio de tejeduría puede ser actualizada.",
        }

    return {"updatable": False, "message": result.error.detail}
