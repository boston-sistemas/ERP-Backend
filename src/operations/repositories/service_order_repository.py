from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import func

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import ServiceOrder


class ServiceOrderRepository(BaseRepository[ServiceOrder]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(ServiceOrder, promec_db, flush)

    def get_load_options(
        self,
        include_detail: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        if include_detail:
            options.append(joinedload(ServiceOrder.detail))

        return options

    async def find_service_orders_by_order_type(
        self,
        order_type: str,
        order_id: str = None,
        period: int = None,
        supplier_ids: list[str] = None,
        include_detail: bool = False,
        include_annulled: bool = False,
        filter: BinaryExpression = None,
        limit: int = None,
        offset: int = None,
        apply_unique: bool = False,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[ServiceOrder]:
        base_filter = (ServiceOrder.company_code == MECSA_COMPANY_CODE) & (
            ServiceOrder._type == order_type
        )

        if not include_annulled:
            base_filter = base_filter & (ServiceOrder.status_flag == "P")

        if order_id:
            base_filter = base_filter & (ServiceOrder.id.like(f"%{order_id}%"))

        if supplier_ids:
            base_filter = base_filter & (ServiceOrder.supplier_id.in_(supplier_ids))

        if period:
            base_filter = base_filter & (func.YEAR(ServiceOrder.issue_date) == period)

        filter = base_filter & filter if filter is not None else base_filter

        options = self.get_load_options(include_detail=include_detail)

        return await self.find_all(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            order_by=order_by,
            apply_unique=True,
        )

    async def find_service_order_by_order_id_and_order_type(
        self,
        order_id: str,
        order_type: str,
        filter: BinaryExpression = None,
        include_detail: bool = False,
    ) -> ServiceOrder | None:
        base_filter = (
            (ServiceOrder.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrder.id == order_id)
            & (ServiceOrder._type == order_type)
        )
        filter = base_filter & filter if filter is not None else base_filter

        options = self.get_load_options(include_detail=include_detail)

        service_order = await self.find(
            filter=filter,
            options=options,
        )

        return service_order
