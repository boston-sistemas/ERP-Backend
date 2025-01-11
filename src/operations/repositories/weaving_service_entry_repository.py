from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.operations.constants import (
    ENTRY_DOCUMENT_CODE,
    ENTRY_MOVEMENT_TYPE,
    WEAVING_SERVICE_ENTRY_MOVEMENT_CODE,
    WEAVING_STORAGE_CODE,
)
from src.operations.models import (
    FabricWarehouse,
    Movement,
    MovementDetail,
)

from .movement_repository import MovementRepository


class WeavingServiceEntryRepository(MovementRepository):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(promec_db, flush)

    @staticmethod
    def get_weaving_service_entry_fields() -> tuple:
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
            Movement.document_note,
            Movement.nrogf,
            Movement.sergf,
            Movement.fecgf,
            Movement.user_id,
            Movement.flgcbd,
            Movement.reference_number1,
        )

    @staticmethod
    def include_details(include_detail_card: bool = True) -> list[Load]:
        base_options = [
            joinedload(Movement.detail)
            .joinedload(MovementDetail.detail_fabric)
            .load_only(
                FabricWarehouse.guide_net_weight,
                FabricWarehouse.roll_count,
                FabricWarehouse.fabric_type,
                FabricWarehouse.tint_color_id,
                FabricWarehouse.tint_supplier_id,
                FabricWarehouse.tint_supplier_color_id,
            )
        ]

        if include_detail_card:
            base_options.append(
                joinedload(Movement.detail).joinedload(MovementDetail.detail_card)
            )

        return base_options

    def get_load_options(
        self,
        include_detail: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        options.append(load_only(*self.get_weaving_service_entry_fields()))

        if include_detail:
            options.extend(self.include_details())

        return options

    async def find_weaving_service_entry_by_entry_number(
        self,
        entry_number: str,
        period: int,
        filter: BinaryExpression = None,
        include_detail_card: bool = True,
        include_detail: bool = False,
    ) -> Movement | None:
        base_filter = (
            (Movement.storage_code == WEAVING_STORAGE_CODE)
            & (Movement.movement_type == ENTRY_MOVEMENT_TYPE)
            & (Movement.movement_code == WEAVING_SERVICE_ENTRY_MOVEMENT_CODE)
            & (Movement.document_code == ENTRY_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options(include_detail=include_detail)

        weaving_service_entry = await self.find_movement_by_document_number(
            document_number=entry_number,
            filter=filter,
            options=options,
        )

        return weaving_service_entry if weaving_service_entry is not None else None

    async def find_weaving_service_entries(
        self,
        period: int,
        include_annulled: bool = False,
        limit: int = None,
        offset: int = None,
        filter: BinaryExpression = None,
    ) -> list[Movement]:
        base_filter = (
            (Movement.storage_code == WEAVING_STORAGE_CODE)
            & (Movement.movement_type == ENTRY_MOVEMENT_TYPE)
            & (Movement.movement_code == WEAVING_SERVICE_ENTRY_MOVEMENT_CODE)
            & (Movement.document_code == ENTRY_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        if not include_annulled:
            base_filter = base_filter & (Movement.status_flag == "P")

        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options()

        weaving_service_entries = await self.find_movements(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            order_by=Movement.creation_date.desc(),
        )

        return weaving_service_entries
