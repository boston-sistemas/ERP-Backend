from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.core.services import PermissionService
from src.security.audit import AuditService

from .supplier_schema import (
    SupplierCreateSupplierColorSchema,
    SupplierFilterParams,
    SupplierSimpleListSchema,
)
from .supplier_service import SupplierService
from .suppliers_colors.supplier_color_schema import (
    SupplierColorListSchema,
    SupplierColorSchema,
)
from .suppliers_colors.supplier_color_service import SupplierColorService

router = APIRouter()


@router.get(
    "/{service_code}",
    response_model=SupplierSimpleListSchema,
    description="Obtén una lista de proveedores según el código del servicio. Códigos disponibles: HIL (Servicio de Hilado), 003 (Servicio de Tejeduria), 004 (Servicio de Tintoreria).",
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_suppliers_by_service(
    request: Request,
    service_code: str,
    filter_params: SupplierFilterParams = Query(SupplierFilterParams()),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierService(promec_db=promec_db)
    result = await service.read_suppliers_by_service(
        service_code=service_code,
        filter_params=filter_params,
    )

    if result.is_success:
        return result.value

    raise result.error


@AuditService.audit_action_log()
@router.get("/colors/{supplier_id}", response_model=SupplierColorListSchema)
async def read_supplier_colors(
    request: Request,
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


@AuditService.audit_action_log()
@router.get("/colors-id/{id}", response_model=SupplierColorSchema)
async def read_supplier_color(
    request: Request,
    id: str,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierColorService(promec_db=promec_db)
    result = await service.read_supplier_color(id=id)

    if result.is_success:
        return result.value

    raise result.error


@AuditService.audit_action_log()
@router.post("/colors-id/", response_model=SupplierColorSchema)
async def create_supplier_color(
    request: Request,
    form: SupplierCreateSupplierColorSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierService(promec_db=promec_db)
    result = await service.create_supplier_color(form=form)

    if result.is_success:
        return result.value

    raise result.error


@AuditService.audit_action_log()
@router.patch("/colors-id/{id}", response_model=SupplierColorSchema)
async def update_supplier_color(
    request: Request,
    id: str,
    form: SupplierCreateSupplierColorSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = SupplierService(promec_db=promec_db)
    result = await service.update_supplier_color(id=id, form=form)

    if result.is_success:
        return result.value

    raise result.error
