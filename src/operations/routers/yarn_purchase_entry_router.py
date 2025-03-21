from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.services import PermissionService
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    YarnPurchaseEntriesSimpleListSchema,
    YarnPurchaseEntryCreateSchema,
    YarnPurchaseEntryFilterParams,
    YarnPurchaseEntryPrintListSchema,
    YarnPurchaseEntrySchema,
    YarnPurchaseEntryUpdateSchema,
)
from src.operations.services import (
    YarnPurchaseEntryService,
)
from src.security.audit import AuditService

router = APIRouter()


@router.get(
    "/",
    response_model=YarnPurchaseEntriesSimpleListSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_yarn_purchase_entries(
    request: Request,
    filter_params: YarnPurchaseEntryFilterParams = Query(
        YarnPurchaseEntryFilterParams()
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(promec_db=promec_db)
    result = await service.read_yarn_purchase_entries(
        filter_params=filter_params,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/search/items-groups-availability", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_yarn_purchase_entries_items_groups_availability(
    request: Request,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    service_order_id: str | None = Query(default=None, alias="serviceOrderId"),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(promec_db=promec_db, db=db)
    result = await service.read_yarn_purchase_entry_item_group_availability(
        period=period,
        service_order_id=service_order_id,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{yarn_purchase_entry_number}",
    response_model=YarnPurchaseEntrySchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_yarn_purchase_entry(
    request: Request,
    yarn_purchase_entry_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(promec_db=promec_db)
    result = await service.read_yarn_purchase_entry(
        yarn_purchase_entry_number=yarn_purchase_entry_number,
        period=period,
        include_details=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.post(
    "/", response_model=YarnPurchaseEntrySchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def create_yarn_purchase_entry(
    request: Request,
    form: YarnPurchaseEntryCreateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(db=db, promec_db=promec_db)
    result = await service.create_yarn_purchase_entry(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch("/{yarn_purchase_entry_number}", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_yarn_purchase_entry(
    request: Request,
    yarn_purchase_entry_number: str,
    form: YarnPurchaseEntryUpdateSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(db=db, promec_db=promec_db)
    result = await service.update_yarn_purchase_entry(
        yarn_purchase_entry_number=yarn_purchase_entry_number,
        period=period,
        form=form,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.put("/{yarn_purchase_entry_number}/anulate", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_yarn_purchase_entry_status(
    request: Request,
    yarn_purchase_entry_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(db=db, promec_db=promec_db)
    result = await service.anulate_yarn_purchase_entry(
        yarn_purchase_entry_number=yarn_purchase_entry_number,
        period=period,
    )

    if result.is_success:
        return {"message": "El ingreso por compra de hilado ha sido anulado con éxito."}

    raise result.error


@router.get(
    "/{yarn_purchase_entry_number}/is-updatable", status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def is_updated_permission(
    request: Request,
    yarn_purchase_entry_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(db=db, promec_db=promec_db)
    result = await service.is_updated_permission(
        yarn_purchase_entry_number=yarn_purchase_entry_number,
        period=period,
    )

    if result.is_success:
        return {
            "updatable": True,
            "message": "El ingreso por compra de hilado puede ser actualizado.",
        }

    return {"updatable": False, "message": result.error.detail}


@router.post("/print/movement", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def print_yarn_purchase_entry(
    request: Request,
    form: YarnPurchaseEntryPrintListSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(db=db, promec_db=promec_db)
    result = await service.print_yarn_purchase_entry(
        # form=form
    )

    if result.is_success:
        response = StreamingResponse(result.value, media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=tarjetas.pdf"
        return response

    raise result.error
