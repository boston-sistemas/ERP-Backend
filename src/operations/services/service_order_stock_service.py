from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import SERVICE_ORDER_STOCK_NOT_FOUND_FAILURE
from src.operations.models import ServiceOrderStock
from src.operations.repositories import ServiceOrderStockRepository

class ServiceOrderStockService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = ServiceOrderStockRepository(promec_db=promec_db)

    async def _read_service_order_stock(
        self,
        product_code: str,
        storage_code: str,
        period: int,
        reference_number: str,
        item_number: int,
    ) -> Result[ServiceOrderStock, CustomException]:
        service_order_stock = await self.repository.find_service_order_stock_by_product_code_and_storage_code_and_reference_number_and_item_number(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number
        )

        if service_order_stock is None:
            return SERVICE_ORDER_STOCK_NOT_FOUND_FAILURE

        return Success(service_order_stock)

    async def rollback_current_stock(
        self,
        storage_code: str,
        period: int,
        product_code: str,
        reference_number: str,
        item_number: int,
        quantity: int,
    ) -> Result[None, CustomException]:

        service_order_stock = await self._read_service_order_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number
        )

        if service_order_stock.is_failure:
            return service_order_stock

        service_order_stock: ServiceOrderStock = service_order_stock.value
        service_order_stock.stkact -= quantity
        await self.repository.save(service_order_stock)

        return Success(None)

    async def update_current_stock(
        self,
        product_code: str,
        storage_code: str,
        period: int,
        reference_number: str,
        item_number: int,
        new_stock: int
    ) -> Result[None, CustomException]:

        service_order_stock = await self._read_service_order_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number
        )

        if service_order_stock.is_failure:
            return service_order_stock

        service_order_stock: ServiceOrderStock = service_order_stock.value
        service_order_stock.stkact += new_stock

        await self.repository.save(service_order_stock)

        return Success(None)

    async def delete_service_order_stock(
        self,
        product_code: str,
        storage_code: str,
        period: int,
        reference_number: str,
        item_number: int,
    ) -> Result[None, CustomException]:

        service_order_stock = await self._read_service_order_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number
        )

        if service_order_stock.is_failure:
            return service_order_stock

        await self.repository.delete(service_order_stock.value)

        return Success(None)

    async def anulate_service_order_stock(
        self,
        product_code: str,
        storage_code: str,
        period: int,
        reference_number: str,
        item_number: int,
    ) -> Result[None, CustomException]:

        service_order_stock = await self._read_service_order_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number
        )

        if service_order_stock.is_failure:
            return service_order_stock

        service_order_stock: ServiceOrderStock = service_order_stock.value
        service_order_stock.status_flag = "A"

        await self.repository.save(service_order_stock)

        return Success(None)
