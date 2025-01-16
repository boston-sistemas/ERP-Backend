from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.operations.schemas import SupplierSimpleListSchema
from src.operations.services import SupplierService

router = APIRouter()


@router.get(
    "/{service_code}",
    response_model=SupplierSimpleListSchema,
    description="Obtén una lista de proveedores según el código del servicio. Códigos disponibles: HIL (Servicio de Hilado), 003 (Servicio de Tejeduria), 004 (Servicio de Tintoreria).",
)
async def read_suppliers_by_service(
    service_code: str,
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_inactives: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierService(promec_db=promec_db)
    result = await service.read_suppliers_by_service(
        service_code=service_code,
        limit=limit,
        offset=offset,
        include_inactives=include_inactives,
        include_other_addresses=True,
    )

    if result.is_success:
        return result.value

    raise result.error
