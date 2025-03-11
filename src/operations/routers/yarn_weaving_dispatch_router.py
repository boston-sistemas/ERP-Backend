from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.services import AuditService, PermissionService
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    YarnWeavingDispatchCreateSchema,
    YarnWeavingDispatchFilterParams,
    YarnWeavingDispatchListSchema,
    YarnWeavingDispatchPrintListSchema,
    YarnWeavingDispatchSchema,
    YarnWeavingDispatchUpdateSchema,
)
from src.operations.services import YarnWeavingDispatchService

router = APIRouter()


@router.get(
    "/", response_model=YarnWeavingDispatchListSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def read_yarn_weaving_dispatches(
    request: Request,
    filter_params: YarnWeavingDispatchFilterParams = Query(
        YarnWeavingDispatchFilterParams()
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
    result = await service.read_yarn_weaving_dispatches(
        filter_params=filter_params,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{yarn_weaving_dispatch_number}",
    response_model=YarnWeavingDispatchSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_yarn_weaving_dispatch(
    request: Request,
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


@router.post(
    "/", response_model=YarnWeavingDispatchSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def create_yarn_weaving_dispatch(
    request: Request,
    form: YarnWeavingDispatchCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = YarnWeavingDispatchService(promec_db=promec_db, db=db)
    result = await service.create_yarn_weaving_dispatch(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch("/{yarn_weaving_dispatch_number}", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_yarn_weaving_dispatch(
    request: Request,
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
        return result.value

    raise result.error


@router.put("/{yarn_weaving_dispatch_number}/anulate", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def update_yarn_weaving_dispatch_status(
    request: Request,
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


@router.get(
    "/{yarn_weaving_dispatch_number}/is-updatable", status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def is_updated_permission(
    request: Request,
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


@router.post("/print/movement", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def print_yarn_weaving_dispatch(
    request: Request,
    form: YarnWeavingDispatchPrintListSchema,
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
