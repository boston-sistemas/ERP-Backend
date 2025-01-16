from datetime import date

from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.operations.constants import (
    YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
    YARN_WEAVING_DISPATCH_STORAGE_CODE,
)
from src.operations.models import Movement, MovementDetail, MovementYarnOCHeavy

from .movement_repository import MovementRepository


class YarnWeavingDispatchRepository(MovementRepository):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(promec_db, flush)

    @staticmethod
    def get_yarn_weaving_dispatch_fields() -> tuple:
        return (
            Movement.storage_code,
            Movement.movement_type,
            Movement.movement_code,
            Movement.document_code,
            Movement.document_number,
            Movement.period,
            Movement.creation_date,
            Movement.creation_time,
            Movement.auxiliary_code,
            Movement.status_flag,
            Movement.reference_number2,
            Movement.document_note,
            Movement.printed_flag,
            Movement.flgcbd,
            Movement.reference_number1,
            Movement.nrodir2,
        )

    @staticmethod
    def include_detail(
        use_contains_eager: bool = False,
    ) -> list[Load]:
        base_options = []
        if not use_contains_eager:
            base_options = [
                joinedload(Movement.detail).joinedload(MovementDetail.detail_aux),
            ]
        else:
            base_options = [
                contains_eager(Movement.detail).contains_eager(
                    MovementDetail.detail_aux
                )
            ]

        return base_options

    def get_load_options(
        self,
        include_detail: bool = False,
        include_detail_entry: bool = False,
        use_contains_eager: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        options.append(load_only(*self.get_yarn_weaving_dispatch_fields()))

        if include_detail:
            options.extend(self.include_detail(use_contains_eager=use_contains_eager))

        if include_detail_entry:
            if use_contains_eager:
                options.append(
                    contains_eager(Movement.detail).contains_eager(
                        MovementDetail.movement_ingress
                    )
                )
            else:
                options.append(
                    joinedload(Movement.detail).joinedload(
                        MovementDetail.movement_ingress
                    )
                )

        return options

    def get_load_joins(
        self,
        include_detail: bool = False,
        include_detail_entry: bool = False,
    ) -> list[tuple]:
        joins: list[tuple] = []

        if include_detail:
            joins.append(Movement.detail)
            joins.append(MovementDetail.detail_aux)

        if include_detail_entry:
            joins.append(MovementDetail.movement_ingress)

        return joins

    async def find_yarn_weaving_dispatch_by_dispatch_number(
        self,
        dispatch_number: str,
        period: int,
        filter: BinaryExpression = None,
        use_outer_joins: bool = False,
        include_detail: bool = False,
        include_detail_entry: bool = False,
    ) -> Movement | None:
        base_filter = (
            (Movement.storage_code == YARN_WEAVING_DISPATCH_STORAGE_CODE)
            & (Movement.movement_type == YARN_WEAVING_DISPATCH_MOVEMENT_TYPE)
            & (Movement.movement_code == YARN_WEAVING_DISPATCH_MOVEMENT_CODE)
            & (Movement.document_code == YARN_WEAVING_DISPATCH_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        filter = base_filter & filter if filter is not None else base_filter

        options = self.get_load_options(
            include_detail=include_detail,
            include_detail_entry=include_detail_entry,
            use_contains_eager=True,
        )

        joins = self.get_load_joins(
            include_detail=include_detail, include_detail_entry=include_detail_entry
        )

        yarn_weaving_dispatch = await self.find_movement_by_document_number(
            document_number=dispatch_number,
            use_outer_joins=use_outer_joins,
            filter=filter,
            joins=joins,
            options=options,
        )

        # print("---", type(yarn_weaving_dispatch.detail[0].movement_ingress.movement_detail))
        # print("---", yarn_weaving_dispatch.detail[0].movement_ingress.ingress_number)

        return yarn_weaving_dispatch

    async def find_yarn_weaving_dispatches(
        self,
        period: int,
        dispatch_number: str = None,
        supplier_ids: list[str] = None,
        start_date: date = None,
        end_date: date = None,
        limit: int = None,
        offset: int = None,
        include_annulled: bool = False,
        filter: BinaryExpression = None,
    ) -> list[Movement]:
        base_filter = (
            (Movement.storage_code == YARN_WEAVING_DISPATCH_STORAGE_CODE)
            & (Movement.movement_type == YARN_WEAVING_DISPATCH_MOVEMENT_TYPE)
            & (Movement.movement_code == YARN_WEAVING_DISPATCH_MOVEMENT_CODE)
            & (Movement.document_code == YARN_WEAVING_DISPATCH_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        if not include_annulled:
            base_filter = base_filter & (Movement.status_flag == "P")

        if dispatch_number:
            base_filter = base_filter & (
                Movement.document_number.like(f"%{dispatch_number}%")
            )

        if supplier_ids:
            base_filter = base_filter & Movement.auxiliary_code.in_(supplier_ids)

        if start_date:
            base_filter = base_filter & (Movement.creation_date >= start_date)

        if end_date:
            base_filter = base_filter & (Movement.creation_date <= end_date)

        filter = base_filter & filter if filter is not None else base_filter

        options = self.get_load_options()

        yarn_weaving_dispatches = await self.find_movements(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            order_by=Movement.creation_date.desc(),
        )

        return yarn_weaving_dispatches
