from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    YarnPurchaseEntriesSimpleListSchema,
    YarnPurchaseEntryCreateSchema,
    YarnPurchaseEntrySchema,
    YarnPurchaseEntryUpdateSchema,
)
from src.operations.services import (
    YarnPurchaseEntryService,
)

router = APIRouter()


@router.get("/", response_model=YarnPurchaseEntriesSimpleListSchema)
async def read_yarn_purchase_entries(
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_inactive: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(promec_db=promec_db)
    result = await service.read_yarn_purchase_entries(
        limit=limit, offset=offset, period=period, include_inactive=include_inactive
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/{yarn_purchase_entry_number}", response_model=YarnPurchaseEntrySchema)
async def read_yarn_purchase_entry(
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


@router.post("/")
async def create_yarn_purchase_entry(
    form: YarnPurchaseEntryCreateSchema,
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(db=db, promec_db=promec_db)
    result = await service.create_yarn_purchase_entry(form=form)

    if result.is_success:
        return {"message": "El ingreso por compra de hilado ha sido creado con éxito."}

    raise result.error


@router.patch("/{yarn_purchase_entry_number}")
async def update_yarn_purchase_entry(
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
        return {
            "message": "El ingreso por compra de hilado ha sido actualizado con éxito."
        }

    raise result.error


@router.put("/{yarn_purchase_entry_number}/anulate")
async def update_yarn_purchase_entry_status(
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


@router.get("/{yarn_purchase_entry_number}/is-updated-permission")
async def is_updated_permission(
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
        return {"message": "El ingreso por compra de hilado puede ser actualizado."}

    raise result.error
