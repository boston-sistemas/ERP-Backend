from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.services import AuditService, PermissionService
from src.security.schemas import (
    ParameterCategoryCreateSchema,
    ParameterCategoryListSchema,
    ParameterCategorySchema,
)
from src.security.services import ParameterCategoryService

router = APIRouter()


@router.get(
    "/{parameter_category_id}",
    response_model=ParameterCategorySchema,
    status_code=status.HTTP_200_OK,
)
@AuditService.audit_action_log()
async def read_parameter_category(
    request: Request, parameter_category_id: int, db: AsyncSession = Depends(get_db)
):
    service = ParameterCategoryService(db=db)
    result = await service.read_parameter_category(parameter_category_id)

    if result.is_success:
        return result.value

    raise result.error


@router.get(
    "/", response_model=ParameterCategoryListSchema, status_code=status.HTTP_200_OK
)
@AuditService.audit_action_log()
async def read_parameter_categories(
    request: Request, db: AsyncSession = Depends(get_db)
):
    service = ParameterCategoryService(db=db)
    result = await service.read_parameter_categories()

    if result.is_success:
        return ParameterCategoryListSchema(parameter_categories=result.value)

    raise result.value


@router.post("/", status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def create_parameter_category(
    request: Request,
    parameter_category_form: ParameterCategoryCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    service = ParameterCategoryService(db=db)
    creation_result = await service.create_parameter_category(
        form=parameter_category_form
    )
    if creation_result.is_success:
        return {"message": "Categoría de parámetro creado con éxito."}

    raise creation_result.error
