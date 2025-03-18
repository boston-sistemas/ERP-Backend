from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import ServiceRate


class RateRepository(BaseRepository[ServiceRate]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ServiceRate, promec_db, flush)

    @staticmethod
    def get_rate_fields() -> tuple:
        return (
            ServiceRate.rate_id,
            ServiceRate.serial_code,
            ServiceRate.supplier_id,
            ServiceRate.fabric_id,
            ServiceRate.currency,
            ServiceRate.rate,
            ServiceRate.period,
            ServiceRate.month_number,
        )

    def get_load_options(
        self,
        include_order_service_detail_rate: bool = False,
    ) -> list[Load]:
        options: list[Load] = []
        options.append(load_only(*self.get_rate_fields()))

        if include_order_service_detail_rate:
            options.append(joinedload(ServiceRate.order_service_detail_rate))

        return options

    async def find_rates(
        self,
        serial_code: str = None,
        supplier_ids: list[str] = None,
        fabric_ids: list[str] = None,
        currency: bool = None,
        period: int = None,
        month_number: int = None,
        limit: int = None,
        offset: int = None,
        filter: BinaryExpression = None,
        joins: list[tuple] = None,
    ) -> list[ServiceRate]:
        base_filter: list[BinaryExpression] = []
        base_filter.append(ServiceRate.company_code == MECSA_COMPANY_CODE)
        base_filter.append(ServiceRate.rate_id != None)

        if serial_code:
            base_filter.append(ServiceRate.serial_code == serial_code)
        if supplier_ids:
            base_filter.append(ServiceRate.supplier_id.in_(supplier_ids))
        if fabric_ids:
            base_filter.append(ServiceRate.fabric_id.in_(fabric_ids))
        if currency is not None:
            base_filter.append(ServiceRate.currency == currency)
        if period:
            base_filter.append(ServiceRate.period == period)
        if month_number:
            base_filter.append(ServiceRate.month_number == month_number)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )
        options = self.get_load_options()

        rates = await self.find_all(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            joins=joins,
            order_by=[
                ServiceRate.rate_id.desc(),
                ServiceRate.period.desc(),
                ServiceRate.month_number.desc(),
            ],
        )

        return rates

    async def find_rate_by_id(
        self,
        rate_id: str,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        joins: list[tuple] = None,
    ) -> ServiceRate | None:
        options = self.get_load_options()
        base_filter: list[BinaryExpression] = []
        base_filter.append(ServiceRate.rate_id == rate_id)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        return await self.find(filter=filter, options=options, joins=joins)
