from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.parameter_settings import param_settings
from src.security.schemas import DataTypeListSchema, FiberCategoriesSchema
from src.security.services import ParameterService

router = APIRouter()


@router.get("/data-types", response_model=DataTypeListSchema)
async def read_datatypes():
    return DataTypeListSchema


@router.get("/fiber-categories", response_model=FiberCategoriesSchema)
async def read_fiber_categories(db: AsyncSession = Depends(get_db)):
    service = ParameterService(db=db)

    result = await service.read_active_parameters_by_category(
        parameter_category_id=param_settings.FIBER_CATEGORY_PARAM_CATEGORY_ID,
        load_only_value=True,
    )

    return FiberCategoriesSchema(fiber_categories=result.value)
