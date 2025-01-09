from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    YarnWeavingDispatchCreateSchema,
    YarnWeavingDispatchSchema,
    YarnWeavingDispatchSimpleListSchema,
    YarnWeavingDispatchUpdateSchema,
)
from src.operations.services import YarnWeavingDispatchService

router = APIRouter()


@router.get("/", response_model=YarnWeavingDispatchSimpleListSchema)
async def read_yarn_weaving_dispatches(
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_inactive: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
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
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
    result = await service.read_yarn_weaving_dispatch(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
        period=period,
        include_detail=True,
        include_detail_entry=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.post("/", response_model=YarnWeavingDispatchSchema)
async def create_yarn_weaving_dispatch(
    form: YarnWeavingDispatchCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
    result = await service.create_yarn_weaving_dispatch(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch("/{yarn_weaving_dispatch_number}")
async def update_yarn_weaving_dispatch(
    yarn_weaving_dispatch_number: str,
    form: YarnWeavingDispatchUpdateSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
    result = await service.update_yarn_weaving_dispatch(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
        form=form,
        period=period,
    )

    if result.is_success:
        return {
            "message": "La salida de hilado ha tejeduría ha sido actualizada exitosamente."
        }

    raise result.error


@router.put("/{yarn_weaving_dispatch_number}/anulate")
async def update_yarn_weaving_dispatch_status(
    yarn_weaving_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)

    result = await service.anulate_yarn_weaving_dispatch(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number, period=period
    )

    if result.is_success:
        return {
            "message": "La salida de hilado ha tejeduría ha sido anulada exitosamente."
        }

    raise result.error


@router.get("/{yarn_weaving_dispatch_number}/is-updatable")
async def is_updated_permission(
    yarn_weaving_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
    result = await service.is_updated_permission(
        yarn_weaving_dispatch_number=yarn_weaving_dispatch_number, period=period
    )

    if result.is_success:
        return {
            "updatable": True,
            "message": "La salida de hilado ha tejeduría puede ser actualizado.",
        }

    return {"updatable": False, "message": result.error.detail}


@router.post("/print/movement")
async def print_yarn_weaving_dispatch(
    # form: WeavingServiceEntryPrintListSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = YarnWeavingDispatchService(db=db, promec_db=promec_db)
    result = await service.print_yarn_weaving_dispatch(
        # form=form
    )

    if result.is_success:
        response = StreamingResponse(result.value, media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=tarjetas.pdf"
        return response

    raise result.error
