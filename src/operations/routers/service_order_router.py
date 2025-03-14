from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.services import PermissionService
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    ServiceOrderCreateSchema,
    ServiceOrderFilterParams,
    ServiceOrderListSchema,
    ServiceOrderProgressReviewListSchema,
    ServiceOrderSchema,
    ServiceOrderUpdateSchema,
)
from src.operations.services import ServiceOrderService
from src.security.audit import AuditService

router = APIRouter()


@router.get("/", response_model=ServiceOrderListSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_service_orders(
    request: Request,
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


@router.get(
    "/progress/review",
    response_model=ServiceOrderProgressReviewListSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_service_orders_in_progress_review(
    request: Request,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.read_service_orders_in_progress_review(
        period=period, limit=limit, offset=offset
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{order_id}", response_model=ServiceOrderSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def read_service_order(
    request: Request,
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


@router.post("/", response_model=ServiceOrderSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def create_weaving_service_order(
    request: Request,
    form: ServiceOrderCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceOrderService(promec_db=promec_db, db=db)
    result = await service.create_weaving_service_order(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch(
    "/{order_id}", response_model=ServiceOrderSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def update_weaving_service_order(
    request: Request,
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


@router.put("/{order_id}/anulate", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def anulate_weaving_service_order(
    request: Request,
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


@router.get("/{order_id}/is-updatable", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def is_updated_permission_weaving_service_order(
    request: Request,
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
