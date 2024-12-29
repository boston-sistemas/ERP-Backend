from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db

from src.operations.services import (
    YarnWeavingDispatchService
)

from src.operations.schemas import (
    YarnWeavingDispatchSimpleListSchema,
    YarnWeavingDispatchSchema,
    YarnWeavingDispatchCreateSchema,
    YarnWeavingDispatchUpdateSchema,
)

from src.core.utils import PERU_TIMEZONE, calculate_time
router = APIRouter()

@router.get("/", response_model=YarnWeavingDispatchSimpleListSchema)
async def read_yarn_weaving_dispatches(
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year,
        ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_inactive: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db)
    result = await service.read_yarn_weaving_dispatches(
        limit=limit, offset=offset, period=period, include_inactive=include_inactive
    )

    if result.is_success:
        return result.value

    raise result.error

@router.get("/{yarn_weaving_dispatch_number}", response_model=YarnWeavingDispatchSchema)
async def read_yarn_weaving_dispatch(
    yarn_weaving_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year,
        ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db)
    result = await service.read_yarn_weaving_dispatch(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
        period=period,
        include_detail=True,
        include_detail_entry=True
    )

    if result.is_success:
        return result.value

    raise result.error

@router.post("/")
async def create_yarn_weaving_dispatch(
    form: YarnWeavingDispatchCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db)
    result = await service.create_yarn_weaving_dispatch(form=form)

    if result.is_success:
        return {"message": "La salida de hilado ha tejeduría ha sido creada exitosamente."}

    raise result.error

@router.patch("/{yarn_weaving_dispatch_number}")
async def update_yarn_weaving_dispatch(
    yarn_weaving_dispatch_number: str,
    form: YarnWeavingDispatchUpdateSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year,
        ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db)
    result = await service.update_yarn_weaving_dispatch(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
        form=form,
        period=period
    )

    if result.is_success:
        return {"message": "La salida de hilado ha tejeduría ha sido actualizada exitosamente."}

    raise result.error

@router.put("/{yarn_weaving_dispatch_number}/anulate")
async def update_yarn_weaving_dispatch_status(
    yarn_weaving_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year,
        ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):

    service = YarnWeavingDispatchService(promec_db=promec_db)

    result = await service.anulate_yarn_weaving_dispatch(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
        period=period
    )

    if result.is_success:
        return {"message": "La salida de hilado ha tejeduría ha sido anulada exitosamente."}

    raise result.error
