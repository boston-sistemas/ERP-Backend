from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db

from src.operations.schemas import (
    YarnPurchaseEntrySchema,
    YarnPurchaseEntriesSimpleListSchema,
    YarnPurchaseEntrySearchSchema
)

from src.operations.services import (
    YarnPurchaseEntryService,
)

router = APIRouter()

@router.post("/", response_model=YarnPurchaseEntriesSimpleListSchema)
async def read_yarn_purchase_entries(
    form: YarnPurchaseEntrySearchSchema,
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(promec_db=promec_db)
    result = await service.read_yarn_purchase_entries(
        limit=limit,
        offset=offset,
        form=form
    )

    if result.is_success:
        return result.value

    raise result.error

@router.post("/{yarn_purchase_entry_number}", response_model=YarnPurchaseEntrySchema)
async def read_yarn_purchase_entry(
    yarn_purchase_entry_number: str,
    form: YarnPurchaseEntrySearchSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnPurchaseEntryService(promec_db=promec_db)
    result = await service.read_yarn_purchase_entry(
        yarn_purchase_entry_number=yarn_purchase_entry_number,
        form=form,
        include_details=True
    )

    if result.is_success:
        return result.value

    raise result.error
