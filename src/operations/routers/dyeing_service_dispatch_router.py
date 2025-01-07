from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.utils import PERU_TIMEZONE, calculate_time

from src.operations.schemas import (
    DyeingServiceDispatchSchema,
    DyeingServiceDispatchesListSchema,
    DyeingServiceDispatchCreateSchema,
    DyeingServiceDispatchUpdateSchema,
)

from src.operations.services import DyeingServiceDispatchService

router = APIRouter()

@router.get("/", response_model=DyeingServiceDispatchesListSchema)
async def read_dyeing_service_dispatches(
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_inactive: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.read_dyeing_service_dispatches(
        limit=limit, offset=offset, period=period, include_inactive=include_inactive
    )

    if result.is_success:
        return result.value

    raise result.error

@router.get("/{dyeing_service_dispatch_number}", response_model=DyeingServiceDispatchSchema)
async def read_dyeing_service_dispatch(
    dyeing_service_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.read_dyeing_service_dispatch(
        dyeing_service_dispatch_number=dyeing_service_dispatch_number,
        period=period,
        include_detail=True,
        include_detail_card=True,
    )

    if result.is_success:
        return result.value

    raise result.error
