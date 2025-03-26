from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db

from .supplier_color_schema import (
    SupplierColorListSchema,
    SupplierColorSchema,
)
from .supplier_color_service import SupplierColorService

router = APIRouter()


@router.get("/{supplier_id}", response_model=SupplierColorListSchema)
async def read_supplier_colors_by_suppliers(
    supplier_id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierColorService(promec_db=promec_db)
    result = await service.read_supplier_colors_by_suppliers(
        supplier_id=supplier_id,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/supplier_color/{id}", response_model=SupplierColorSchema)
async def read_supplier_color(
    id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierColorService(promec_db=promec_db)
    result = await service.read_supplier_color(id=id)

    if result.is_success:
        return result.value

    raise result.error
