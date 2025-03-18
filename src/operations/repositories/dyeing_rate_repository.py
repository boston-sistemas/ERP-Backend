from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import SERVICE_CODE_SUPPLIER_DYEING
from src.core.repository import RateRepository
from src.operations.models import ServiceRate


class DyeingRepository(RateRepository):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ServiceRate, db, flush)

    @staticmethod
    def get_dyeing_rate_fields() -> tuple:
        fields = RateRepository.get_rate_fields()
        fields += (ServiceRate.color_id,)
        return fields

    def get_load_options(self) -> list[Load]:
        options: list[Load] = []
        options.append(load_only(*self.get_dyeing_rate_fields()))

        return options

    async def find_dyeing_rate_by_id(
        self,
        rate_id: str,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        joins: list[tuple] = None,
    ) -> ServiceRate | None:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []
        base_filter.append(ServiceRate.rate_id == rate_id)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )
        options = self.get_load_options()

        dyeing_rate = await self.find_rate_by_id(
            filter=filter, options=options, joins=joins
        )

        return dyeing_rate

    async def find_dyeing_rates(
        self,
        color_id: str = None,
        supplier_ids: str = None,
        fabric_id: str = None,
        limit: int = None,
        offset: int = None,
        filter: BinaryExpression = None,
        joins: list[tuple] = None,
    ) -> list[ServiceRate]:
        base_filter = list[BinaryExpression] = []

        if supplier_ids:
            base_filter = base_filter & ServiceRate.supplier_id.in_(supplier_ids)
        if color_id:
            base_filter = base_filter.append(ServiceRate.color_id == color_id)

        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options()

        dyeing_rates = await self.find_rates(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            joins=joins,
            color_id=color_id,
            fabric_id=fabric_id,
            supplier_ids=supplier_ids,
        )

        return dyeing_rates
