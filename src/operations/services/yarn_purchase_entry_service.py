from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.operations.failures import (
    YARN_PURCHASE_ENTRY_CONE_COUNT_MISMATCH_FAILURE,
    YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE,
    YARN_PURCHASE_ENTRY_PACKAGE_COUNT_MISMATCH_FAILURE,
    YARN_PURCHASE_ENTRY_YARN_NOT_FOUND_FAILURE,
)
from src.operations.models import (
    Movement,
    SupplierSequenceManager,
)
from src.operations.repositories import (
    YarnPurchaseEntryRepository,
)
from src.operations.schemas import (
    OrdenCompraWithDetallesSchema,
    YarnPurchaseEntriesSimpleListSchema,
    YarnPurchaseEntryCreateSchema,
    YarnPurchaseEntryDetalleCreateSchema,
    YarnPurchaseEntrySchema,
    YarnPurchaseEntrySearchSchema,
)
from src.operations.services import OrdenCompraService, YarnService


class YarnPurchaseEntryService:
    def __init__(self, promec_db: AsyncSession, db: AsyncSession = None) -> None:
        self.promec_db = promec_db
        self.repository = YarnPurchaseEntryRepository(promec_db)
        self.yarn_service = YarnService(promec_db=promec_db, db=db)
        self.purchase_order_service = OrdenCompraService(db=promec_db)
        self.supplier_sequence_manager = BaseRepository[SupplierSequenceManager]

    async def _read_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        form: YarnPurchaseEntrySearchSchema,
        include_details: bool = False,
    ) -> Result[Movement, CustomException]:
        yarn_purchase_entry = await self.repository.find_yarn_purchase_by_entry_number(
            purchase_entry_number=yarn_purchase_entry_number,
            form=form,
            include_details=include_details,
        )

        if yarn_purchase_entry is None:
            return YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE

        return Success(yarn_purchase_entry)

    async def read_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        form: YarnPurchaseEntrySearchSchema,
        include_details: bool = False,
    ) -> Result[YarnPurchaseEntrySchema, CustomException]:
        yarn_purchase_entry_result = await self._read_yarn_purchase_entry(
            yarn_purchase_entry_number=yarn_purchase_entry_number,
            form=form,
            include_details=include_details,
        )

        if yarn_purchase_entry_result.is_failure:
            return yarn_purchase_entry_result

        return Success(
            YarnPurchaseEntrySchema.model_validate(yarn_purchase_entry_result.value)
        )

    async def read_yarn_purchase_entries(
        self,
        form: YarnPurchaseEntrySearchSchema,
        limit: int = None,
        offset: int = None,
    ) -> Result[YarnPurchaseEntriesSimpleListSchema, CustomException]:
        yarn_purchase_entries = await self.repository.find_yarn_purchase_entries(
            limit=limit,
            offset=offset,
            form=form,
        )

        return Success(
            YarnPurchaseEntriesSimpleListSchema(
                yarn_purchase_entries=yarn_purchase_entries
            )
        )

    async def _validate_yarn_purchase_entry_data(
        self,
        data: YarnPurchaseEntryCreateSchema,
    ) -> Result[None, CustomException]:
        yarn_order = await self.purchase_order_service.read_purchase_yarn_order(
            purchase_order_number=data.purchase_order_number, include_detalle=True
        )

        if yarn_order.is_failure:
            return yarn_order

        return yarn_order

    async def _validate_yarn_purchase_entry_detalle_data(
        self,
        data: list[YarnPurchaseEntryDetalleCreateSchema],
        purchase_yarn_order: OrdenCompraWithDetallesSchema,
    ) -> Result[None, CustomException]:
        detalle_yarn_ids = [detail.yarn.id for detail in purchase_yarn_order.detail]

        for detail in data:
            if detail.yarn_id not in detalle_yarn_ids:
                return YARN_PURCHASE_ENTRY_YARN_NOT_FOUND_FAILURE

            if detail.detail_heavy:
                cone_count_total = sum(
                    [cone.cone_count for cone in detail.detail_heavy]
                )
                if detail.guide_cone_count < cone_count_total:
                    return YARN_PURCHASE_ENTRY_CONE_COUNT_MISMATCH_FAILURE

                package_count_total = sum(
                    [cone.package_count for cone in detail.detail_heavy]
                )
                if detail.guide_package_count < package_count_total:
                    return YARN_PURCHASE_ENTRY_PACKAGE_COUNT_MISMATCH_FAILURE

        return Success(None)

    # async def _read_next_value(
    #     self,
    #     supplier: str,
    # ) -> Result[int, CustomException]:
    #

    async def create_yarn_purchase_entry(
        self,
        form: YarnPurchaseEntryCreateSchema,
    ) -> Result[None, CustomException]:
        validation_result = await self._validate_yarn_purchase_entry_data(data=form)

        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_yarn_purchase_entry_detalle_data(
            data=form.detail, purchase_yarn_order=validation_result.value
        )

        if validation_result.is_failure:
            return validation_result

        # supplier_sequence = await self.supplier_sequence_manager.find(
        #     form
        # )

        return Success(None)
