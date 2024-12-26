from sqlalchemy.ext.asyncio import AsyncSession
from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success

from src.operations.models import (
    CurrencyExchange,
    Movement,
    MovementDetail,
    MovementDetailAux,
    MovementYarnOCHeavy,
)

from src.operations.repositories import (
    YarnPurchaseEntryDetailHeavyRepository
)

from src.operations.failures import (
    YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE,
)

from src.operations.schemas import (
    YarnPurchaseEntryDetailHeavySchema
)

class YarnPurchaseEntryDetailHeavyService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = YarnPurchaseEntryDetailHeavyRepository(promec_db)

    async def _read_yarn_purchase_entry_detail_heavy(
        self,
        ingress_number: str,
        item_number: int,
        group_number: int,
        period: int,
        include_detail_entry: bool = False,
    ) -> Result[MovementYarnOCHeavy, CustomException]:
        yarn_purchase_entry_detail_heavy = await self.repository.find_yarn_purchase_entry_detail_heavy_by_ingress_number_and_item_and_group_(
            ingress_number=ingress_number,
            item_number=item_number,
            group_number=group_number,
            period=period,
            include_detail_entry=include_detail_entry,
        )

        if yarn_purchase_entry_detail_heavy is None:
            return YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE

        return Success(yarn_purchase_entry_detail_heavy)

    async def read_yarn_purchase_entry_detail_heavy(
        self,
        ingress_number: str,
        item_number: int,
        group_number: int,
        period: int,
        include_detail_entry: bool = False,
    ) -> Result[MovementYarnOCHeavy, CustomException]:
        yarn_purchase_entry_detail_heavy_result = await self._read_yarn_purchase_entry_detail_heavy(
            ingress_number=ingress_number,
            item_number=item_number,
            group_number=group_number,
            period=period,
            include_detail_entry=include_detail_entry,
        )

        if yarn_purchase_entry_detail_heavy_result.is_failure:
            return yarn_purchase_entry_detail_heavy_result

        return Success(
            YarnPurchaseEntryDetailHeavySchema.model_validate(
                yarn_purchase_entry_detail_heavy_result.value
            )
        )

