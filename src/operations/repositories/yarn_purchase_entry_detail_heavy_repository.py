from typing import Sequence

from sqlalchemy import BinaryExpression, Integer, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, load_only, with_loader_criteria
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import (
    Movement,
    MovementDetail,
    MovementYarnOCHeavy,
)


class YarnPurchaseEntryDetailHeavyRepository(BaseRepository[MovementYarnOCHeavy]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(MovementYarnOCHeavy, promec_db, flush)

    @staticmethod
    def get_yarn_purchase_entry_detail_heavy_fields() -> tuple:
        return (
            MovementYarnOCHeavy.group_number,
            MovementYarnOCHeavy.item_number,
            MovementYarnOCHeavy.ingress_number,
            MovementYarnOCHeavy.period,
            MovementYarnOCHeavy.exit_number,
            MovementYarnOCHeavy.cone_count,
            MovementYarnOCHeavy.package_count,
            MovementYarnOCHeavy.net_weight,
            MovementYarnOCHeavy.gross_weight,
            MovementYarnOCHeavy.packages_left,
            MovementYarnOCHeavy.cones_left,
            MovementYarnOCHeavy.status_flag,
            MovementYarnOCHeavy.dispatch_status,
            MovementYarnOCHeavy.entry_user_id,
            MovementYarnOCHeavy.exit_user_id,
            MovementYarnOCHeavy.destination_storage,
            MovementYarnOCHeavy.supplier_yarn_id,
            MovementYarnOCHeavy.supplier_batch,
        )

    async def find_yarn_purchase_entry_detail_heavy_by_ingress_number_and_item_and_group(
        self,
        ingress_number: str,
        item_number: int,
        group_number: int,
        period: int,
        include_detail_entry: bool = False,
        include_entry_movement: bool = False,
        include_entry_movement_detail: bool = False,
        include_entry_movement_detail_heavy: bool = False,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        **kwargs,
    ) -> MovementYarnOCHeavy | None:
        options: list[Load] = []
        joins: list[tuple] = []

        if include_detail_entry:
            joins.append(MovementYarnOCHeavy.movement_detail)

        base_filter = (
            (MovementYarnOCHeavy.company_code == MECSA_COMPANY_CODE)
            & (MovementYarnOCHeavy.ingress_number == ingress_number)
            & (MovementYarnOCHeavy.item_number == item_number)
            & ((cast(MovementYarnOCHeavy.group_number, Integer)) == group_number)
            & (MovementYarnOCHeavy.period == period)
        )

        options.append(load_only(*self.get_yarn_purchase_entry_detail_heavy_fields()))
        if include_detail_entry:
            base_filter = base_filter & (MovementDetail.period == period)

            options.append(contains_eager(MovementYarnOCHeavy.movement_detail))

        if include_entry_movement:
            options.append(joinedload(MovementYarnOCHeavy.movement))

            if include_entry_movement_detail:
                options.append(
                    joinedload(MovementYarnOCHeavy.movement)
                    .joinedload(Movement.detail)
                    .joinedload(MovementDetail.detail_aux)
                )

                if include_entry_movement_detail_heavy:
                    options.append(
                        joinedload(MovementYarnOCHeavy.movement)
                        .joinedload(Movement.detail)
                        .joinedload(MovementDetail.detail_heavy)
                    )

        filter = base_filter & filter if filter is not None else base_filter

        return await self.find(
            filter=filter,
            options=options,
            joins=joins,
            **kwargs,
        )

    async def find_yarn_purchase_entries_items_groups_availability(
        self,
        period: int,
        include_detail_entry: bool = False,
        include_entry: bool = False,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        **kwargs,
    ) -> list[MovementYarnOCHeavy]:
        options: list[Load] = []
        joins: list[tuple] = []

        if include_detail_entry:
            joins.append(MovementYarnOCHeavy.movement_detail)

        base_filter = (MovementYarnOCHeavy.company_code == MECSA_COMPANY_CODE) & (
            MovementYarnOCHeavy.dispatch_status == False
        )

        options.append(load_only(*self.get_yarn_purchase_entry_detail_heavy_fields()))
        if include_detail_entry:
            base_filter = base_filter & (MovementDetail.period == period)

            options.append(contains_eager(MovementYarnOCHeavy.movement_detail))

        filter = base_filter & filter if filter is not None else base_filter

        return await self.find_all(
            filter=filter,
            options=options,
            joins=joins,
            order_by=MovementYarnOCHeavy.ingress_number.desc(),
            **kwargs,
        )
