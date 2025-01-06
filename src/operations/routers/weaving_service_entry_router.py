from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    WeavingServiceEntriesSimpleListSchema,
    WeavingServiceEntryCreateSchema,
    WeavingServiceEntrySchema,
)
from src.operations.services import (
    WeavingServiceEntryService,
)

router = APIRouter()


@router.get("/", response_model=WeavingServiceEntriesSimpleListSchema)
async def read_weaving_service_entries(
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_inactive: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db)
    result = await service.read_weaving_service_entries(
        limit=limit, offset=offset, period=period, include_inactive=include_inactive
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/{weaving_service_entry_number}", response_model=WeavingServiceEntrySchema)
async def read_weaving_service_entry(
    weaving_service_entry_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db)
    result = await service.read_weaving_service_entry(
        weaving_service_entry_number=weaving_service_entry_number,
        period=period,
        include_detail=True,
        include_detail_card=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", response_model=WeavingServiceEntrySchema)
async def create_weaving_service_entry(
    weaving_service_entry: WeavingServiceEntryCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db, db=db)
    result = await service.create_weaving_service_entry(form=weaving_service_entry)

    if result.is_success:
        return result.value

    raise result.error
