from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import (
    ParameterCreateSchema,
    ParameterWithCategoryListSchema,
    ParameterWithCategorySchema,
)
from src.security.services import ParameterService

router = APIRouter()


@router.get("/{parameter_id}", response_model=ParameterWithCategorySchema)
async def read_parameter(parameter_id: int, db: AsyncSession = Depends(get_db)):
    parameter_service = ParameterService(db=db)
    result = await parameter_service.read_parameter(
        parameter_id=parameter_id, include_category=True
    )

    if result.is_success:
        return result.value

    raise result.error


@router.get("/", response_model=ParameterWithCategoryListSchema)
async def read_parameters(db: AsyncSession = Depends(get_db)):
    parameter_service = ParameterService(db=db)
    result = await parameter_service.read_parameters(include_category=True)

    if result.is_success:
        return ParameterWithCategoryListSchema(parameters=result.value)

    raise result.error


@router.post("/")
async def create_parameter(
    form: ParameterCreateSchema, db: AsyncSession = Depends(get_db)
):
    parameter_service = ParameterService(db=db)
    creation_result = await parameter_service.create_parameter(form)

    if creation_result.is_success:
        return {"message": "Parámetro creado con éxito."}

    raise creation_result.error
