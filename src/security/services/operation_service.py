from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import OperationFailures
from src.security.repositories import OperationRepository
from src.security.schemas import (
    OperationListSchema,
    OperationSchema,
)


class OperationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db
        self.repository: OperationRepository = OperationRepository(db=db)

    async def read_operations(self) -> Result[OperationListSchema, CustomException]:
        operations: list[OperationSchema] = await self.repository.find_operations()
        return Success(OperationListSchema(operations=operations))

    async def _read_operation(
        self, operation_id: int
    ) -> Result[OperationSchema, CustomException]:
        operation: OperationSchema = await self.repository.find_operation_by_id(
            id=operation_id
        )

        if operation is None:
            return OperationFailures.OPERATION_NOT_FOUND_FAILURE

        return Success(operation)

    async def read_operation(
        self, operation_id: int
    ) -> Result[OperationSchema, CustomException]:
        operation: Success = await self._read_operation(operation_id)

        if operation.is_failure:
            return operation

        return Success(OperationSchema.model_validate(operation.value))
