from typing import Sequence, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import Movement, MovementDetail


class MovementRepository(BaseRepository[Movement]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Movement, promec_db, flush)
        self.movement_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )

    async def find_movement_by_document_number(
        self,
        document_number: str,
        use_outer_joins: bool = False,
        filter: BinaryExpression = None,
        joins: list[tuple] = None,
        options: list[Load] = None,
        include_detail: bool = False,
        **kwargs,
    ) -> Movement | None:
        options = options or []
        base_filter = (Movement.company_code == MECSA_COMPANY_CODE) & (
            Movement.document_number == document_number
        )
        filter = base_filter & filter if filter is not None else base_filter

        if include_detail:
            options.append(joinedload(Movement.detail))

        return await self.find(
            filter=filter,
            joins=joins,
            use_outer_joins=use_outer_joins,
            options=options,
            **kwargs,
        )

    async def find_movements(
        self,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        apply_unique: bool = False,
        joins: list[tuple] = None,
        limit: int = None,
        offset: int = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[Movement]:
        base_filter = Movement.company_code == MECSA_COMPANY_CODE
        filter = base_filter & filter if filter is not None else base_filter

        return await self.find_all(
            filter=filter,
            options=options,
            joins=joins,
            apply_unique=apply_unique,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )

    async def find_movements_detail(
        self,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        apply_unique: bool = False,
        limit: int = None,
        offset: int = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[MovementDetail]:
        base_filter = MovementDetail.company_code == MECSA_COMPANY_CODE
        filter = base_filter & filter if filter is not None else base_filter

        return await self.movement_detail_repository.find_all(
            filter=filter,
            options=options,
            apply_unique=apply_unique,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )

    async def find_max_item_number_by_movement(
        self,
        storage_code: str,
        movement_type: str,
        movement_code: str,
        document_code: str,
        document_number: str,
        period: int,
    ) -> int:
        base_filter = (
            (MovementDetail.company_code == MECSA_COMPANY_CODE)
            & (MovementDetail.storage_code == storage_code)
            & (MovementDetail.movement_type == movement_type)
            & (MovementDetail.movement_code == movement_code)
            & (MovementDetail.document_code == document_code)
            & (MovementDetail.document_number == document_number)
            & (MovementDetail.period == period)
        )
        movement_detail = await self.movement_detail_repository.find_all(
            filter=base_filter,
            order_by=MovementDetail.item_number.desc(),
            limit=1,
        )

        if len(movement_detail) == 0:
            return 1

        return movement_detail[0].item_number
