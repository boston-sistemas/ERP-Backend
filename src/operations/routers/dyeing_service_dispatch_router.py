from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.services import AuditService, PermissionService
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    DyeingServiceDispatchCreateSchema,
    DyeingServiceDispatchesListSchema,
    DyeingServiceDispatchSchema,
    DyeingServiceDispatchUpdateSchema,
)
from src.operations.services import DyeingServiceDispatchService

router = APIRouter()


@router.get(
    "/",
    response_model=DyeingServiceDispatchesListSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_dyeing_service_dispatches(
    request: Request,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    limit: int | None = Query(default=10, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
    include_annulled: bool | None = Query(default=False),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.read_dyeing_service_dispatches(
        limit=limit, offset=offset, period=period, include_annulled=include_annulled
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{dyeing_service_dispatch_number}",
    response_model=DyeingServiceDispatchSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_dyeing_service_dispatch(
    request: Request,
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


@router.post(
    "/", response_model=DyeingServiceDispatchSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def create_dyeing_service_dispatch(
    request: Request,
    form: DyeingServiceDispatchCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.create_dyeing_service_dispatch(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch(
    "/{dyeing_service_dispatch_number}",
    response_model=DyeingServiceDispatchSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def update_dyeing_service_dispatch(
    request: Request,
    dyeing_service_dispatch_number: str,
    form: DyeingServiceDispatchUpdateSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.update_dyeing_service_dispatch(
        dyeing_service_dispatch_number=dyeing_service_dispatch_number,
        period=period,
        form=form,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.put("/{dyeing_service_dispatch_number}/anulate", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def anulate_dyeing_service_dispatch(
    request: Request,
    dyeing_service_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.anulate_dyeing_service_dispatch(
        dyeing_service_dispatch_number=dyeing_service_dispatch_number, period=period
    )

    if result.is_success:
        return {
            "message": "La salida al servicio de tintorería ha sido anulada exitosamente."
        }

    raise result.error


@router.get(
    "/{dyeing_service_dispatch_number}/is-updatable", status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def check_dyeing_service_dispatch_is_updatable(
    request: Request,
    dyeing_service_dispatch_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = DyeingServiceDispatchService(promec_db=promec_db, db=db)
    result = await service.is_updated_permission(
        dyeing_service_dispatch_number=dyeing_service_dispatch_number, period=period
    )

    if result.is_success:
        return {
            "updatable": True,
            "message": "La salida al servicio de tintorería puede ser actualizada.",
        }

    return {"updatable": False, "message": result.error.detail}


@router.post("/print/movement", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def print_dyeing_service_dispatch(
    request: Request,
    # form: WeavingServiceEntryPrintListSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    db: AsyncSession = Depends(get_db),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = DyeingServiceDispatchService(db=db, promec_db=promec_db)
    result = await service.print_dyeing_service_dispatch(
        # form=form
    )

    if result.is_success:
        response = StreamingResponse(result.value, media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=tarjetas.pdf"
        return response

    raise result.error
