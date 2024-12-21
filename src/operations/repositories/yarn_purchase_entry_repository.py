from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.operations.constants import (
    YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
    YARN_PURCHASE_ENTRY_MOVEMENT_CODE,
    YARN_PURCHASE_ENTRY_MOVEMENT_TYPE,
    YARN_PURCHASE_ENTRY_STORAGE_CODE,
)
from src.operations.models import (
    Movement,
    MovementDetail,
    MovementDetail,
    OrdenCompra,
    OrdenCompraDetalle,
)

from src.operations.schemas import YarnPurchaseEntrySearchSchema

from .movement_repository import MovementRepository


class YarnPurchaseEntryRepository(MovementRepository):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(promec_db, flush)

    @staticmethod
    def get_yarn_purchase_entry_fields() -> tuple:
        return (
            Movement.storage_code,
            Movement.movement_type,
            Movement.movement_code,
            Movement.document_code,
            Movement.document_number,
            Movement.period,
            Movement.creation_date,
            Movement.creation_time,
            Movement.currency_code,
            Movement.exchange_rate,
            Movement.document_note,
            Movement.auxiliary_code,
            Movement.status_flag,
            Movement.user_id,
            Movement.reference_number,
            Movement.nrogf,
            Movement.sergf,
            Movement.fecgf,
            Movement.annulment_date,
            Movement.annulment_user_id,
            Movement.serial_number,
            Movement.printed_flag,
            Movement.flgtras,
            Movement.voucher_number,
            Movement.fchcp,
            Movement.flgcbd,
            Movement.origin_station,
            Movement.transaction_mode,
            Movement.supplier_batch,
            Movement.mecsa_batch,
        )

    @staticmethod
    def include_details(include_heavy: bool = True) -> list[Load]:
        base_options = [
            joinedload(Movement.detail).joinedload(MovementDetail.detail_aux)
        ]

        if include_heavy:
            base_options.append(
                joinedload(Movement.detail).joinedload(MovementDetail.detail_heavy)
            )

        return base_options

    def get_load_options(
        self,
        include_details: bool = False,
        include_purchase_order: bool = False,
        include_purchase_order_detail: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        if include_details:
            options.extend(self.include_details())

        if include_purchase_order:
            options.append(joinedload(Movement.purchase_order))
            if include_purchase_order_detail:
                options.append(
                    joinedload(Movement.purchase_order).joinedload(
                        OrdenCompra.detail
                    ).joinedload(OrdenCompraDetalle.yarn)
                )

        options.append(load_only(*self.get_yarn_purchase_entry_fields()))
        return options

    async def find_yarn_purchase_by_entry_number(
        self,
        purchase_entry_number: str,
        period: int,
        filter: BinaryExpression = None,
        include_details: bool = False,
        include_purchase_order: bool = False,
        include_purchase_order_detail: bool = False,
    ) -> Movement | None:
        base_filter = (
            (Movement.storage_code == YARN_PURCHASE_ENTRY_STORAGE_CODE)
            & (Movement.movement_type == YARN_PURCHASE_ENTRY_MOVEMENT_TYPE)
            & (Movement.movement_code == YARN_PURCHASE_ENTRY_MOVEMENT_CODE)
            & (Movement.document_code == YARN_PURCHASE_ENTRY_DOCUMENT_CODE)
            & (Movement.period == period)
        )

        filter = base_filter & filter if filter is not None else base_filter

        options = self.get_load_options(
            include_details=include_details,
            include_purchase_order=include_purchase_order,
            include_purchase_order_detail=include_purchase_order_detail,
        )

        yarn_purchase_entry = await self.find_movement_by_document_number(
            document_number=purchase_entry_number,
            filter=filter,
            options=options,
        )

        return yarn_purchase_entry if yarn_purchase_entry is not None else None

    async def find_yarn_purchase_entries(
        self,
        period: int,
        include_inactive: bool,
        limit: int = None,
        offset: int = None,
        filter: BinaryExpression = None,
    ) -> list[Movement]:
        base_filter = (
            (Movement.storage_code == YARN_PURCHASE_ENTRY_STORAGE_CODE)
            & (Movement.movement_type == YARN_PURCHASE_ENTRY_MOVEMENT_TYPE)
            & (Movement.movement_code == YARN_PURCHASE_ENTRY_MOVEMENT_CODE)
            & (Movement.document_code == YARN_PURCHASE_ENTRY_DOCUMENT_CODE)
            & (Movement.period == period)
        )
        if not include_inactive:
            base_filter = base_filter & (Movement.status_flag == 'P')
        filter = base_filter & filter if filter is not None else base_filter
        options = self.get_load_options()

        yarn_purchase_entries = await self.find_movements(
            filter=filter,
            options=options,
            limit=limit,
            offset=offset,
            order_by=Movement.creation_date.desc(),
        )

        return yarn_purchase_entries
