from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.models import ServiceRate
from src.operations.repositories import RateRepository
from src.operations.schemas import (
    RateSchema,
)


class RateService:
    pass

    def __init__(self, db: AsyncSession) -> None:
        self.repository = RateRepository(db)

    async def _read_service_rate(
        self, rate_id: str
    ) -> Result[ServiceRate, CustomException]:
        service_rate = await self.repository.find_service_rate_by_id(
            rate_id=rate_id,
        )

        if service_rate is None:
            pass
            # return AGREGAR FAILURE

        return Success(service_rate)

    async def read_service_rate(
        self, rate_id: str
    ) -> Result[ServiceRate, CustomException]:
        service_rate_result = await self._read_rate_operation(
            rate_id=rate_id,
        )

        if service_rate_result.is_failure:
            return service_rate_result

        return Success(RateSchema.model_validate(service_rate_result.value))

    async def read_service_rate_by_id(
        self,
        rate_ids: list[str],
    ) -> Result[ServiceRate, CustomException]:
        service_rates = []
        for rate_id in rate_ids:
            service_rate_result = await self.read_rate(rate_id=rate_id)

            if service_rate_result.is_failure:
                continue

            service_rates.append(service_rate_result.value)

        return Success(service_rates)
