from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.operations.constants import (
    WEAVING_STORAGE_CODE,
    DISPATCH_MOVEMENT_TYPE,
    DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
    DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
)
from src.operations.models import (
    FabricWarehouse,
    Movement,
    MovementDetail,
)

from .movement_repository import MovementRepository

class DyeingServiceDispatchRepository(MovementRepository):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(promec_db, flush)

    @staticmethod
    def get_dyeing_service_dispatch_fields() -> tuple:
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
            Movement.document_note,
            Movement.user_id,
            Movement.empqnro2,
            Movement.nrodir2,
            Movement.status_flag,
        )

    @staticmethod
    def include_detail(include_detail_card: bool = False) -> list[Load]:
        base_options = []

        base_options.append(
            joinedload(Movement.detail_dyeing)
            .load_only(
                FabricWarehouse.guide_net_weight,
                FabricWarehouse.roll_count,
                FabricWarehouse.product_id,
                FabricWarehouse.mecsa_weight,
            )
        )

        return base_options

    def get_load_options(
        self,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> list[Load]:
        options: list[Load] = []
        options.append(load_only(*self.get_dyeing_service_dispatch_fields()))

        if include_detail:
            options.extend(self.include_detail(
                include_detail_card=include_detail_card
            ))

            if include_detail_card:
                options.append(
                    joinedload(Movement.detail_dyeing).joinedload(FabricWarehouse.detail_card)
                )

        return options

    async def find_dyeing_service_dispatches(
        self,
        period: int,
        include_inactive: bool = False,
        include_detail: bool = False,
        include_detail_card: bool = False,
        limit: int = None,
        offset: int = None,
        filter: BinaryExpression = None,
    ) -> Movement:

        base_filter = (
            (Movement.storage_code == WEAVING_STORAGE_CODE)
            & (Movement.movement_type == DISPATCH_MOVEMENT_TYPE)
            & (Movement.movement_code == DYEING_SERVICE_DISPATCH_MOVEMENT_CODE)
            & (Movement.document_code == DYEING_SERVICE_DISPATCH_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        if not include_inactive:
            base_filter = base_filter & (Movement.status_flag == "P")

        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options(
            include_detail=include_detail,
            include_detail_card=include_detail_card
        )

        dyeing_service_dispatches = await self.find_movements(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            order_by=[Movement.document_number.desc()]
        )

        return dyeing_service_dispatches

    async def find_dyeing_service_dispatch_by_dispatch_number(
        self,
        dispatch_number: str,
        period: int,
        filter: BinaryExpression = None,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Movement | None:
        base_filter = (
            (Movement.storage_code == WEAVING_STORAGE_CODE)
            & (Movement.movement_type == DISPATCH_MOVEMENT_TYPE)
            & (Movement.movement_code == DYEING_SERVICE_DISPATCH_MOVEMENT_CODE)
            & (Movement.document_code == DYEING_SERVICE_DISPATCH_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options(
            include_detail=include_detail,
            include_detail_card=include_detail_card
        )

        dyeing_service_dispatch = await self.find_movement_by_document_number(
            document_number=dispatch_number,
            filter=filter,
            options=options,
        )

        return dyeing_service_dispatch if dyeing_service_dispatch is not None else None
