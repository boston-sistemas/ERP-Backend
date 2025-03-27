from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.services import PermissionService
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.schemas import (
    WeavingServiceEntriesListSchema,
    WeavingServiceEntryCreateSchema,
    WeavingServiceEntryFilterParams,
    WeavingServiceEntryOptionsParams,
    WeavingServiceEntryPrintListSchema,
    WeavingServiceEntrySchema,
    WeavingServiceEntryUpdateSchema,
)
from src.operations.services import (
    WeavingServiceEntryService,
)
from src.security.audit import AuditService

router = APIRouter()


@router.get(
    "/", response_model=WeavingServiceEntriesListSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def read_weaving_service_entries(
    request: Request,
    filter_params: WeavingServiceEntryFilterParams = Query(
        WeavingServiceEntryFilterParams()
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db)
    result = await service.read_weaving_service_entries(
        filter_params=filter_params,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/{weaving_service_entry_number}",
    response_model=WeavingServiceEntrySchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_weaving_service_entry(
    request: Request,
    weaving_service_entry_number: str,
    options_params: WeavingServiceEntryOptionsParams = Query(
        WeavingServiceEntryOptionsParams()
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db)
    result = await service.read_weaving_service_entry(
        weaving_service_entry_number=weaving_service_entry_number,
        options_params=options_params,
        include_detail=True,
        include_detail_card=True,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.post(
    "/", response_model=WeavingServiceEntrySchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def create_weaving_service_entry(
    request: Request,
    form: WeavingServiceEntryCreateSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db, db=db)
    result = await service.create_weaving_service_entry(form=form)

    if result.is_success:
        return result.value

    raise result.error


@router.patch(
    "/{weaving_service_entry_number}",
    response_model=WeavingServiceEntrySchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def update_weaving_service_entry(
    request: Request,
    weaving_service_entry_number: str,
    form: WeavingServiceEntryUpdateSchema,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db, db=db)
    result = await service.update_weaving_service_entry(
        weaving_service_entry_number=weaving_service_entry_number,
        form=form,
        period=period,
    )

    if result.is_success:
        return result.value

    raise result.error


@router.put("/{weaving_service_entry_number}/anulate", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def anulate_weaving_service_entry(
    request: Request,
    weaving_service_entry_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
    db: AsyncSession = Depends(get_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db, db=db)
    result = await service.anulate_weaving_service_entry(
        weaving_service_entry_number=weaving_service_entry_number, period=period
    )

    if result.is_success:
        return {
            "message": "El ingreso de servicio de tejeduría ha sido anulada exitosamente."
        }

    raise result.error


@router.get(
    "/{weaving_service_entry_number}/is-updatable", status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def check_weaving_service_entry_is_updatable(
    request: Request,
    weaving_service_entry_number: str,
    period: int | None = Query(
        default=calculate_time(tz=PERU_TIMEZONE).date().year, ge=2000
    ),
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db)
    result = await service.is_updated_permission(
        weaving_service_entry_number=weaving_service_entry_number, period=period
    )

    if result.is_success:
        return {
            "updatable": True,
            "message": "El ingreso de servicio de tejeduría puede ser actualizado.",
        }

    return {
        "updatable": False,
        "message": result.error.detail,
    }


@router.post("/print/cards", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def print_weaving_service_entry(
    request: Request,
    form: WeavingServiceEntryPrintListSchema,
    promec_db: AsyncSession = Depends(get_promec_db),
):
    service = WeavingServiceEntryService(promec_db=promec_db)
    result = await service.print_weaving_service_entry(form=form)

    if result.is_success:
        response = StreamingResponse(result.value, media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=tarjetas.pdf"
        return response

    raise result.error
