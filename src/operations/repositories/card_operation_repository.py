from typing import Sequence

from sqlalchemy import BinaryExpression, Integer, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, load_only
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import CardOperation

class CardOperationRepository(BaseRepository[CardOperation]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(CardOperation, promec_db, flush)

    @staticmethod
    def get_card_operation_fields() -> tuple:
        return (
            CardOperation.id,
            CardOperation.fabric_id,
            CardOperation.net_weight,
            CardOperation.tint_supplier_id,
            CardOperation.tint_color_id,
            CardOperation.yarn_supplier_id,
            CardOperation.card_type,
            CardOperation.status_flag,
            CardOperation.exit_number,
            CardOperation.document_number,
            CardOperation.product_id,
        )

    async def find_card_operation_by_id(
        self,
        id: str,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        **kwargs,
    ) -> CardOperation | None:
        options: list[Load] = []

        base_filter = (
            (CardOperation.company_code == MECSA_COMPANY_CODE)
            & (CardOperation.id == id)
        )

        filter = filter if filter is not None else base_filter

        return await self.find(
            filter=filter,
            options=options,
            **kwargs,
        )
