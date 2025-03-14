from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.services import PermissionService
from src.security.audit import AuditService
from src.security.schemas import (
    ParameterCreateSchema,
    ParameterWithCategoryListSchema,
    ParameterWithCategorySchema,
)
from src.security.services import ParameterService

router = APIRouter()


@router.get(
    "/{parameter_id}",
    response_model=ParameterWithCategorySchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_parameter(parameter_id: int, db: AsyncSession = Depends(get_db)):
    parameter_service = ParameterService(db=db)
    result = await parameter_service.read_parameter(
        parameter_id=parameter_id, include_category=True
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/", response_model=ParameterWithCategoryListSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def read_parameters(request: Request, db: AsyncSession = Depends(get_db)):
    parameter_service = ParameterService(db=db)
    result = await parameter_service.read_parameters(include_category=True)

    if result.is_success:
        return ParameterWithCategoryListSchema(parameters=result.value)

    raise result.error


@router.post("/", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def create_parameter(
    request: Request, form: ParameterCreateSchema, db: AsyncSession = Depends(get_db)
):
    parameter_service = ParameterService(db=db)
    creation_result = await parameter_service.create_parameter(form)

    if creation_result.is_success:
        return {"message": "Parámetro creado con éxito."}

    raise creation_result.error
