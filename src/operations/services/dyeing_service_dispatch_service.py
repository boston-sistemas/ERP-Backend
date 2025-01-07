from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.repository import (
    BaseRepository,
)
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from .movement_service import MovementService

from src.operations.repositories import (
    DyeingServiceDispatchRepository,
)

from src.operations.failures import (
    DYEING_SERVICE_DISPATCH_NOT_FOUND_FAILURE,
)

from src.operations.schemas import (
    DyeingServiceDispatchSchema,
    DyeingServiceDispatchesListSchema,
    DyeingServiceDispatchUpdateSchema,
    DyeingServiceDispatchCreateSchema,
)

from src.operations.models import (
    Movement,
    MovementDetail,
)

class DyeingServiceDispatchService(MovementService):
    def __init__(self, promec_db: AsyncSession, db: AsyncSession) -> None:
        super().__init__(promec_db=promec_db)
        self.repository = DyeingServiceDispatchRepository(promec_db=promec_db)

    async def read_dyeing_service_dispatches(
        self,
        period: int,
        limit: int = None,
        offset: int = None,
        include_inactive: bool = False,
    ) -> Result[DyeingServiceDispatchesListSchema, CustomException]:
        dyeing_service_dispatches = await self.repository.find_dyeing_service_dispatches(
            period=period,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive,
        )

        return Success(
            DyeingServiceDispatchesListSchema(
                dyeing_service_dispatches=dyeing_service_dispatches
            )
        )

    async def _read_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[Movement, CustomException]:
        dyeing_service_dispatch = (
            await self.repository.find_dyeing_service_dispatch_by_dispatch_number(
                dispatch_number=dyeing_service_dispatch_number,
                period=period,
                include_detail=include_detail,
                include_detail_card=include_detail_card,
            )
        )

        if dyeing_service_dispatch is None:
            return DYEING_SERVICE_DISPATCH_NOT_FOUND_FAILURE

        return Success(dyeing_service_dispatch)

    async def read_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[DyeingServiceDispatchSchema, CustomException]:
        dyeing_service_dispatch = await self._read_dyeing_service_dispatch(
            dyeing_service_dispatch_number=dyeing_service_dispatch_number,
            period=period,
            include_detail=include_detail,
            include_detail_card=include_detail_card,
        )

        if dyeing_service_dispatch.is_failure:
            return dyeing_service_dispatch

        return Success(
            DyeingServiceDispatchSchema.model_validate(dyeing_service_dispatch.value)
        )

