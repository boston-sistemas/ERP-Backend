from fastapi import APIRouter

from src.security.schemas import DataTypeListSchema

router = APIRouter()


@router.get("/data-types", response_model=DataTypeListSchema)
async def read_datatypes():
    return DataTypeListSchema
