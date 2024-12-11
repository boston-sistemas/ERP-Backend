from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success

from src.operations.models import (
    Movement
)

from src.operations.schemas import (
    YarnPurchaseEntrySchema,
    YarnPurchaseEntriesSimpleListSchema,
    YarnPurchaseEntrySearchSchema
)

from src.operations.repositories import (
    YarnPurchaseEntryRepository,
)

from src.operations.failures import (
    YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE
)

class YarnPurchaseEntryService:
    def __init__(self, promec_db: AsyncSession):
        self.promec_db = promec_db
        self.repository = YarnPurchaseEntryRepository(promec_db)

    async def _read_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        form: YarnPurchaseEntrySearchSchema,
        include_details: bool = False,
    ) -> Result[Movement, CustomException]:

        yarn_purchase_entry = await self.repository.find_yarn_purchase_by_entry_number(
            purchase_entry_number=yarn_purchase_entry_number,
            form=form,
            include_details=include_details,
        )

        if yarn_purchase_entry is None:
            return YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE

        return Success(yarn_purchase_entry)

    async def read_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        form: YarnPurchaseEntrySearchSchema,
        include_details: bool = False,
    ) -> Result[YarnPurchaseEntrySchema, CustomException]:
        yarn_purchase_entry_result = await self._read_yarn_purchase_entry(
            yarn_purchase_entry_number=yarn_purchase_entry_number,
            form=form,
            include_details=include_details,
        )

        if yarn_purchase_entry_result.is_failure:
            return yarn_purchase_entry_result

        return Success(
            YarnPurchaseEntrySchema.model_validate(yarn_purchase_entry_result.value)
        )

    async def read_yarn_purchase_entries(
        self,
        form: YarnPurchaseEntrySearchSchema,
        limit: int = None,
        offset: int = None,
    ) -> Result[YarnPurchaseEntriesSimpleListSchema, CustomException]:
        yarn_purchase_entries = await self.repository.find_yarn_purchase_entries(
            limit=limit,
            offset=offset,
            form=form,
        )

        return Success(
            YarnPurchaseEntriesSimpleListSchema(
                yarn_purchase_entries=yarn_purchase_entries
            )
        )
