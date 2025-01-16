from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    OrdenCompraWithDetallesListSchema,
    YarnPurchaseOrderSchema,
)
from src.operations.services import OrdenCompraService

router = APIRouter(
    tags=["Area Operaciones - Ordenes de Compra"],
    prefix="/orden-compra",
)


@router.get("/yarns", response_model=OrdenCompraWithDetallesListSchema)
async def get_ordenes_yarns(
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_promec_db),
):
    orden_service = OrdenCompraService(db)
    ordenes = await orden_service.read_purchase_yarn_orders(
        period=period, include_detalle=True
    )

    return OrdenCompraWithDetallesListSchema(ordenes=ordenes)


@router.get("/yarns/{id}", response_model=YarnPurchaseOrderSchema)
async def read_yarn_order(
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
