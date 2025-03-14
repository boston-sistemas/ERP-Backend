from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.core.services import PermissionService
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    YarnPurchaseOrderListSchema,
    YarnPurchaseOrderSchema,
)
from src.operations.services import OrdenCompraService
from src.security.audit import AuditService

router = APIRouter(
    tags=["Area Operaciones - Ordenes de Compra"],
    prefix="/orden-compra",
)


@router.get(
    "/yarns", response_model=YarnPurchaseOrderListSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def get_ordenes_yarns(
    request: Request,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    include_detail: bool = Query(default=False, alias="includeDetail"),
    db: AsyncSession = Depends(get_promec_db),
):
    service = OrdenCompraService(db)
    result = await service.read_purchase_yarn_orders(
        period=period, include_detalle=include_detail
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/yarns/{id}",
    response_model=YarnPurchaseOrderSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_yarn_order(
    request: Request,
    id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = OrdenCompraService(promec_db)
    result = await service.read_purchase_yarn_order(
        purchase_order_number=id,
        include_detalle=True,
    )

    if result.is_success:
        return result.value

    raise result.error
