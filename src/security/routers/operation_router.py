from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import OperationListSchema
from src.security.services import OperationService

router = APIRouter()


@router.get("/", response_model=OperationListSchema)
async def read_operations(db: AsyncSession = Depends(get_db)):
    operation_service = OperationService(db=db)

    operations = await operation_service.read_operations()

    if operations.is_success:
        return operations.value

    raise operations.error
