from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time

from src.operations.repositories import (
    CardOperationRepository,
)

from src.operations.failures import (
    CARD_OPERATION_NOT_FOUND_FAILURE,
)

from src.operations.schemas import (
    CardOperationSchema,
)

from src.operations.models import CardOperation

class CardOperationService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.repository = CardOperationRepository(promec_db=promec_db)

    async def _read_card_operation(
        self, id: str
    ) -> Result[CardOperation, CustomException]:
        card_operation = await self.repository.find_card_operation_by_id(
            id=id,
        )

        if card_operation is None:
            return CARD_OPERATION_NOT_FOUND_FAILURE

        return Success(card_operation)

    async def read_card_operation(
        self,
        id: str,
    ) -> Result[CardOperationSchema, CustomException]:
        card_operation_result = await self._read_card_operation(
            id=id
        )

        if card_operation_result.is_failure:
            return card_operation_result

        return Success(
            CardOperationSchema.model_validate(
                card_operation_result.value
            )
        )
