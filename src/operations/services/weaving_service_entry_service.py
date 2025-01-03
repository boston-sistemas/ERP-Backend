from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE,
)
from src.operations.models import (
    Movement,
)
from src.operations.repositories import WeavingServiceEntryRepository
from src.operations.schemas import (
    WeavingServiceEntriesSimpleListSchema,
    WeavingServiceEntrySchema,
)

from .movement_service import MovementService


class WeavingServiceEntryService(MovementService):
    def __init__(self, promec_db: AsyncSession) -> None:
        super().__init__(promec_db=promec_db)
        self.repository = WeavingServiceEntryRepository(promec_db=promec_db)

    async def read_weaving_service_entries(
        self,
        period: int,
        limit: int = None,
        offset: int = None,
        include_inactive: bool = False,
    ) -> Result[WeavingServiceEntriesSimpleListSchema, CustomException]:
        weaving_service_entries = await self.repository.find_weaving_service_entries(
            limit=limit,
            offset=offset,
            period=period,
            include_inactive=include_inactive,
        )

        return Success(
            WeavingServiceEntriesSimpleListSchema(
                weaving_service_entries=weaving_service_entries
            )
        )

    async def _read_weaving_service_entry(
        self,
        weaving_service_entry_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[Movement, CustomException]:
        weaving_service_entry = (
            await self.repository.find_weaving_service_entry_by_entry_number(
                entry_number=weaving_service_entry_number,
                period=period,
                include_detail=include_detail,
                include_detail_card=include_detail_card,
            )
        )

        if weaving_service_entry is None:
            return WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE

        return Success(weaving_service_entry)

    async def read_weaving_service_entry(
        self,
        weaving_service_entry_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[WeavingServiceEntrySchema, CustomException]:
        weaving_service_entry_result = await self._read_weaving_service_entry(
            weaving_service_entry_number=weaving_service_entry_number,
            period=period,
            include_detail=include_detail,
            include_detail_card=include_detail_card,
        )

        if weaving_service_entry_result.is_failure:
            return weaving_service_entry_result

        return Success(
            WeavingServiceEntrySchema.model_validate(weaving_service_entry_result.value)
        )
