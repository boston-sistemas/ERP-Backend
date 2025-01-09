from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    CARD_OPERATION_NOT_FOUND_FAILURE,
)
from src.operations.models import CardOperation
from src.operations.repositories import (
    CardOperationRepository,
)
from src.operations.schemas import (
    CardOperationListSchema,
    CardOperationSchema,
)

from .supplier_service import SupplierService


class CardOperationService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.repository = CardOperationRepository(promec_db=promec_db)
        self.supplier_service = SupplierService(promec_db=promec_db)

    async def _read_card_operation(
        self, id: str
    ) -> Result[CardOperation, CustomException]:
        card_operation = await self.repository.find_card_operation_by_id(
            id=id,
        )

        if card_operation is None:
            return CARD_OPERATION_NOT_FOUND_FAILURE

        return Success(card_operation)

    async def read_card_operation(
        self,
        id: str,
    ) -> Result[CardOperationSchema, CustomException]:
        card_operation_result = await self._read_card_operation(id=id)

        if card_operation_result.is_failure:
            return card_operation_result

        return Success(CardOperationSchema.model_validate(card_operation_result.value))

    async def reads_card_operation_by_id(
        self,
        ids: list[str],
    ) -> Result[CardOperationListSchema, CustomException]:
        card_operations = []
        for id in ids:
            card_operation_result = await self.read_card_operation(id=id)

            if card_operation_result.is_failure:
                continue

            card_operations.append(card_operation_result.value)

        suppliers_tint = {
            card.tint_supplier_id: ""
            for card in card_operations
            if card.tint_supplier_id
        }
        suppliers_weaving = {
            card.supplier_weaving_tej: ""
            for card in card_operations
            if card.supplier_weaving_tej
        }
        suppliers_yarn = {
            supplier: ""
            for card in card_operations
            for supplier in card.suppliers_yarn
            if supplier
        }

        suppliers = {**suppliers_tint, **suppliers_weaving, **suppliers_yarn}

        suppliers_result = await self.supplier_service.reads_supplier_initials_by_id(
            ids=suppliers
        )
        if suppliers_result.is_failure:
            return suppliers_result

        suppliers = suppliers_result.value

        for card in card_operations:
            if card.tint_supplier_id:
                card._supplier_tint_initials = suppliers.get(card.tint_supplier_id, "")
            else:
                card._supplier_tint_initials = " "
            if card.supplier_weaving_tej:
                card._supplier_weaving_tej_initials = suppliers.get(
                    card.supplier_weaving_tej, ""
                )
            else:
                card._supplier_weaving_tej_initials = " "

            if card.suppliers_yarn:
                card._supplier_yarn_initials = [
                    suppliers.get(supplier, "") for supplier in card.suppliers_yarn
                ]
            else:
                card._supplier_yarn_initials = []

            print(card.service_orders)
        return Success(CardOperationListSchema(card_operations=card_operations))
