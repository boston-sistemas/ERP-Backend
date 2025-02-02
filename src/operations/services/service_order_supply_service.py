from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import SERVICE_ORDER_SUPPLY_STOCK_NOT_FOUND_FAILURE
from src.operations.models import ServiceOrderSupplyDetail
from src.operations.repositories import ServiceOrderSupplyDetailRepository
from src.operations.schemas import FabricSchema


class ServiceOrderSupplyDetailService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = ServiceOrderSupplyDetailRepository(promec_db=promec_db)

    async def _read_service_order_supply_stock(
        self,
        # product_code: str,
        storage_code: str,
        reference_number: str,
        item_number: int,
    ) -> Result[ServiceOrderSupplyDetail, CustomException]:
        service_order_supply_stock = (
            await self.repository.find_service_order_supply_stock_by_id(
                # product_code=product_code,
                storage_code=storage_code,
                reference_number=reference_number,
                item_number=item_number,
            )
        )

        if service_order_supply_stock is None:
            return SERVICE_ORDER_SUPPLY_STOCK_NOT_FOUND_FAILURE

        return Success(service_order_supply_stock)

    async def _read_service_orders_supply_stock(
        self,
        storage_code: str,
        period: int,
        service_order_id: str,
    ) -> Result[ServiceOrderSupplyDetail, CustomException]:
        service_orders_stock = await self.repository.find_service_order_supply_stocks_by_service_order_id_and_storage_code(
            storage_code=storage_code,
            period=period,
            service_order_id=service_order_id,
        )

        return Success(service_orders_stock)

    async def _read_max_item_number_by_id_service_order_supply_stock(
        self,
        storage_code: str,
        service_order_id: str,
        supply_id: str,
    ) -> Result[ServiceOrderSupplyDetail, CustomException]:
        service_orders_supply_stock_result = (
            await self.repository.find_service_orders_supply_stock(
                storage_code=storage_code,
                service_order_id=service_order_id,
                supply_id=supply_id,
                limit=1,
                order_by=ServiceOrderSupplyDetail.item_number.desc(),
            )
        )

        service_orders_supply_stock: list[ServiceOrderSupplyDetail] = (
            service_orders_supply_stock_result
        )
        if len(service_orders_supply_stock) == 0:
            return Success(0)

        return Success(service_orders_supply_stock[0].item_number)

    async def upsert_service_order_supply_stock(
        self,
        service_order_supply_stock: ServiceOrderSupplyDetail,
    ) -> Result[ServiceOrderSupplyDetail, CustomException]:
        service_orders_supply_stock_result = (
            await self.repository.find_service_orders_supply_stock(
                storage_code=service_order_supply_stock.storage_code,
                service_order_id=service_order_supply_stock.reference_number,
                order_by=ServiceOrderSupplyDetail.item_number.desc(),
            )
        )
        service_orders_supply_stock: list[ServiceOrderSupplyDetail] = (
            service_orders_supply_stock_result
        )

        if len(service_orders_supply_stock) == 0:
            item_number = 1
            service_order_supply_stock.item_number = item_number

            await self.repository.save(service_order_supply_stock, flush=True)
            await self.repository.expunge(service_order_supply_stock)

            return Success(service_order_supply_stock)

        item_number = service_orders_supply_stock[0].item_number + 1

        for service_order_supply in service_orders_supply_stock:
            if (
                service_order_supply.supply_id == service_order_supply_stock.supply_id
            ) and (
                service_order_supply.supplier_yarn_id
                == service_order_supply_stock.supplier_yarn_id
            ):
                service_order_supply.current_stock += (
                    service_order_supply_stock.current_stock
                )
                service_order_supply.provided_quantity += (
                    service_order_supply_stock.provided_quantity
                )
                service_order_supply.quantity_dispatched += (
                    service_order_supply_stock.quantity_dispatched
                )

                await self.repository.save(service_order_supply, flush=True)
                await self.repository.expunge(service_order_supply)

                return Success(service_order_supply)

        service_order_supply_stock.item_number = item_number

        await self.repository.save(service_order_supply_stock, flush=True)
        await self.repository.expunge(service_order_supply_stock)

        return Success(service_order_supply_stock)

    async def rollback_current_stock(
        self,
        storage_code: str,
        # product_code: str,
        reference_number: str,
        item_number: int,
        quantity: int,
    ) -> Result[None, CustomException]:
        service_order_supply_stock = await self._read_service_order_supply_stock(
            # product_code=product_code,
            storage_code=storage_code,
            reference_number=reference_number,
            item_number=item_number,
        )

        if service_order_supply_stock.is_failure:
            return service_order_supply_stock

        service_order_supply_stock: ServiceOrderSupplyDetail = (
            service_order_supply_stock.value
        )
        service_order_supply_stock.current_stock -= quantity
        service_order_supply_stock.provided_quantity -= quantity
        service_order_supply_stock.quantity_dispatched -= quantity
        await self.repository.save(service_order_supply_stock, flush=True)

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
        service_order_supply_stock = await self._read_service_order_supply_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number,
        )

        if service_order_supply_stock.is_failure:
            return service_order_supply_stock

        service_order_supply_stock: ServiceOrderSupplyDetail = (
            service_order_supply_stock.value
        )
        service_order_supply_stock.current_stock += new_stock

        await self.repository.save(service_order_supply_stock, flush=True)

        return Success(None)

    async def _update_remaining_supply_stock_by_yarn(
        self,
        service_orders_stock: list[ServiceOrderSupplyDetail],
        yarn_id: str,
        quantity: int,
    ) -> Result[None, CustomException]:
        for service_order_supply_stock in service_orders_stock:
            if service_order_supply_stock.supply_id == yarn_id:
                if service_order_supply_stock.current_stock <= 0:
                    continue

                if quantity <= 0:
                    break

                if service_order_supply_stock.current_stock <= quantity:
                    quantity -= service_order_supply_stock.current_stock
                    service_order_supply_stock.current_stock = 0
                    service_order_supply_stock.quantity_received += quantity
                else:
                    service_order_supply_stock.current_stock -= quantity
                    service_order_supply_stock.quantity_received += quantity
                    quantity = 0
                await self.repository.save(service_order_supply_stock, flush=True)

        if quantity > 0:
            if service_orders_stock:
                if service_orders_stock[-1].product_code == yarn_id:
                    service_orders_stock[-1].current_stock = max(
                        service_orders_stock[-1].current_stock - quantity, 0
                    )
                    service_orders_stock[-1].quantity_received += quantity
                    await self.repository.save(service_orders_stock[-1], flush=True)
        return Success(None)

    async def _rollback_remaining_supply_stock_by_yarn(
        self,
        service_orders_stock: list[ServiceOrderSupplyDetail],
        yarn_id: str,
        quantity: int,
    ) -> Result[None, CustomException]:
        for service_order_supply_stock in service_orders_stock:
            if service_order_supply_stock.supply_id == yarn_id:
                if quantity <= 0:
                    break

                if (
                    service_order_supply_stock.current_stock
                    == service_order_supply_stock.provided_quantity
                ):
                    continue

                if (
                    service_order_supply_stock.current_stock + quantity
                    <= service_order_supply_stock.provided_quantity
                ):
                    service_order_supply_stock.current_stock += quantity
                    service_order_supply_stock.quantity_received -= quantity
                    quantity = 0
                else:
                    quantity -= (
                        service_order_supply_stock.provided_quantity
                        - service_order_supply_stock.stkact
                    )
                    service_order_supply_stock.current_stock = (
                        service_order_supply_stock.provided_quantity
                    )
                    service_order_supply_stock.quantity_received -= (
                        service_order_supply_stock.provided_quantity
                        - service_order_supply_stock.stkact
                    )

                await self.repository.save(service_order_supply_stock, flush=True)

        if quantity > 0:
            if service_order_supply_stock:
                service_order_supply_stock[-1].current_stock += quantity
                service_order_supply_stock[-1].quantity_received -= quantity
                await self.repository.save(service_order_supply_stock[-1], flush=True)

        return Success(service_orders_stock)

    async def rollback_current_stock_by_fabric_recipe(
        self,
        fabric: FabricSchema,
        quantity: int,
        service_orders_stock: list[ServiceOrderSupplyDetail],
    ) -> Result[None, CustomException]:
        service_orders_stock = sorted(
            service_orders_stock,
            key=lambda x: (
                x.item_number is None,
                x.item_number if x.item_number is not None else float("inf"),
            ),
        )
        for yarn in fabric.recipe:
            quantity_yarn = (yarn.proportion / 100.0) * quantity

            rollback_result = await self._rollback_remaining_supply_stock_by_yarn(
                service_orders_stock=service_orders_stock,
                yarn_id=yarn.yarn_id,
                quantity=quantity_yarn,
            )

            if rollback_result.is_failure:
                print(rollback_result.error)

            service_orders_stock = rollback_result.value

        return Success(service_orders_stock)

    async def update_current_stock_by_fabric_recipe(
        self,
        fabric: FabricSchema,
        quantity: int,
        service_orders_stock: list[ServiceOrderSupplyDetail],
    ) -> Result[None, CustomException]:
        service_orders_stock = sorted(
            service_orders_stock,
            key=lambda x: (
                x.item_number is None,
                x.item_number if x.item_number is not None else float("inf"),
            ),
        )
        for yarn in fabric.recipe:
            quantity_yarn = (yarn.proportion / 100.0) * quantity

            update_result = await self._update_remaining_supply_stock_by_yarn(
                service_orders_stock=service_orders_stock,
                yarn_id=yarn.yarn_id,
                quantity=quantity_yarn,
            )

            if update_result.is_failure:
                print(update_result.error)

        return Success(None)

    async def delete_service_order_supply_stock(
        self,
        product_code: str,
        storage_code: str,
        period: int,
        reference_number: str,
        item_number: int,
    ) -> Result[None, CustomException]:
        service_order_supply_stock = await self._read_service_order_supply_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number,
        )

        if service_order_supply_stock.is_failure:
            return service_order_supply_stock

        await self.repository.delete(service_order_supply_stock.value, flush=True)

        return Success(None)

    async def annul_service_order_supply_stock(
        self,
        product_code: str,
        storage_code: str,
        period: int,
        reference_number: str,
        item_number: int,
    ) -> Result[None, CustomException]:
        service_order_supply_stock = await self._read_service_order_supply_stock(
            product_code=product_code,
            storage_code=storage_code,
            period=period,
            reference_number=reference_number,
            item_number=item_number,
        )

        if service_order_supply_stock.is_failure:
            return service_order_supply_stock

        service_order_supply_stock: ServiceOrderSupplyDetail = (
            service_order_supply_stock.value
        )
        service_order_supply_stock.status_flag = "A"

        await self.repository.save(service_order_supply_stock, flush=True)

        return Success(None)
