from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.loaders import FiberCategories
from src.security.schemas import DataTypeListSchema, FiberCategoriesSchema

router = APIRouter()


@router.get("/data-types", response_model=DataTypeListSchema)
async def read_datatypes():
    return DataTypeListSchema


@router.get("/fiber-categories", response_model=FiberCategoriesSchema)
async def read_fiber_categories(db: AsyncSession = Depends(get_db)):
    return FiberCategoriesSchema(
        fiber_categories=await FiberCategories(db=db).get(actives_only=True)
    )
