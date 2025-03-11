from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.services import AuditService, PermissionService
from src.security.schemas import OperationListSchema
from src.security.services import OperationService

router = APIRouter()


@router.get("/", response_model=OperationListSchema, status_code=status.HTTP_200_OK)
@AuditService.audit_action_log()
async def read_operations(request: Request, db: AsyncSession = Depends(get_db)):
    operation_service = OperationService(db=db)

    operations = await operation_service.read_operations()

    if operations.is_success:
        return operations.value

    raise operations.error
