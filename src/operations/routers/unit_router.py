from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_promec_db
from src.core.services import PermissionService
from src.operations.schemas import DerivedUnitListSchema, UnitListSchema, UnitSchema
from src.operations.services import UnitService
from src.security.audit import AuditService

router = APIRouter()


@router.get("/{code}", response_model=UnitSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_base_unit(
    request: Request, code: str, promec_db: AsyncSession = Depends(get_promec_db)
):
    service = UnitService(promec_db=promec_db)

    result = await service.read_base_unit(code=code, include_derived_units=True)
    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=UnitListSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_base_units(
    request: Request, promec_db: AsyncSession = Depends(get_promec_db)
):
    service = UnitService(promec_db=promec_db)

    result = await service.read_base_units(include_derived_units=True)
    if result.is_success:
        return UnitListSchema(units=result.value)

    raise result.error


@router.get(
    "/{base_code}/derived-units",
    response_model=DerivedUnitListSchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_derived_units_by_base_code(
    request: Request, base_code: str, promec_db: AsyncSession = Depends(get_promec_db)
):
    service = UnitService(promec_db=promec_db)
    result = await service.read_derived_units_by_base_code(base_code=base_code)
    if result.is_success:
        return DerivedUnitListSchema(derived_units=result.value)

    raise result.error
