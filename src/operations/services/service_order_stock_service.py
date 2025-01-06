from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import SERVICE_ORDER_STOCK_NOT_FOUND_FAILURE
from src.operations.models import ServiceOrderStock
from src.operations.repositories import ServiceOrderStockRepository
from src.operations.schemas import FabricSchema


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
            item_number=item_number,
        )

        if service_order_stock is None:
            return SERVICE_ORDER_STOCK_NOT_FOUND_FAILURE

        return Success(service_order_stock)

    async def _reads_service_orders_stock(
        self,
        storage_code: str,
        period: int,
        service_order_id: str,
    ) -> Result[ServiceOrderStock, CustomException]:
        service_orders_stock = await self.repository.find_service_order_stocks_by_service_order_id_and_storage_code(
            storage_code=storage_code,
            period=period,
            service_order_id=service_order_id,
        )

        return Success(service_orders_stock)

    async def _read_max_item_number_by_product_id_and_service_order_id(
        self,
        storage_code: str,
        period: int,
        service_order_id: str,
        product_id: str,
    ) -> Result[ServiceOrderStock, CustomException]:
        service_orders_stock = await self.repository.find_service_order_stocks_by_service_order_id_and_storage_code_and_product_id(
            storage_code=storage_code,
            period=period,
            service_order_id=service_order_id,
            product_id=product_id,
            limit=1,
            order_by=ServiceOrderStock.item_number.desc(),
        )

        if len(service_orders_stock) == 0:
            return Success(1)

        return Success(service_orders_stock[0].item_number)

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
            item_number=item_number,
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
        new_stock: int,
    ) -> Result[None, CustomException]:
        service_order_stock = await self._read_service_order_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number,
        )

        if service_order_stock.is_failure:
            return service_order_stock

        service_order_stock: ServiceOrderStock = service_order_stock.value
        service_order_stock.stkact += new_stock

        await self.repository.save(service_order_stock)

        return Success(None)

    async def _update_remaining_amount_orders_stock_by_yarn(
        self,
        service_orders_stock: list[ServiceOrderStock],
        yarn_id: str,
        quantity: int,
    ) -> Result[None, CustomException]:
        for service_orders_stock in service_orders_stock:
            if service_orders_stock.product_code == yarn_id:
                if quantity <= 0:
                    break

                if service_orders_stock.stkact <= quantity:
                    quantity -= service_orders_stock.stkact
                    service_orders_stock.stkact = 0
                else:
                    service_orders_stock.stkact -= quantity
                    quantity = 0
                await self.repository.save(service_orders_stock)
        return Success(None)

    async def update_current_stock_by_fabric_recipe(
        self,
        fabric: FabricSchema,
        quantity: int,
        service_orders_stock: list[ServiceOrderStock],
    ) -> Result[None, CustomException]:
        for yarn in fabric.recipe:
            quantity_yarn = (yarn.proportion / 100.0) * quantity

            update_result = await self._update_remaining_amount_orders_stock_by_yarn(
                service_orders_stock=service_orders_stock,
                yarn_id=yarn.yarn_id,
                quantity=quantity_yarn,
            )

            if update_result.is_failure:
                print(update_result.error)

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
            item_number=item_number,
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
            item_number=item_number,
        )

        if service_order_stock.is_failure:
            return service_order_stock

        service_order_stock: ServiceOrderStock = service_order_stock.value
        service_order_stock.status_flag = "A"

        await self.repository.save(service_order_stock)

        return Success(None)
