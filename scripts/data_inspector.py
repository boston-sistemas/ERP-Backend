from loguru import logger
from sqlalchemy import (
    Engine,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.operations.models import (
    Movement,
    ServiceOrder,
)
from src.operations.repositories import (
    ServiceOrderRepository,
    YarnPurchaseEntryRepository,
    YarnWeavingDispatchRepository,
)


class DataInspector:
    def __init__(self, promec_engine: Engine, pcp_engine) -> None:
        self.promec_engine = promec_engine
        self.pcp_engine = pcp_engine

    async def inspect_period_yarn_weaving_dispatches(self, period: int) -> None:
        async with AsyncSession(bind=self.promec_engine) as session:
            yarn_repository = YarnWeavingDispatchRepository(session)
            yarn_weaving_dispatches: list[
                Movement
            ] = await yarn_repository.find_yarn_weaving_dispatches(
                period=period,
                include_detail=True,
                apply_unique=True,
            )

            logger.info(
                f"Cantidad de registros encontrados: {len(yarn_weaving_dispatches)} en el periodo {period}"
            )

            for dispatch in yarn_weaving_dispatches:
                # logger.info(f"Detalles encontrados: {len(dispatch.detail)}")
                if len(dispatch.detail) > 1:
                    logger.info(
                        f"El registro con id {dispatch.document_number} en el period {period} tiene más de un detalle: {len(dispatch.detail)}"
                    )
                    print("->", dispatch)
                # logger.info(len(dispatch.detail))
                print(dispatch)

    async def inspect_period_service_orders_weaving(self, period: int) -> None:
        async with AsyncSession(bind=self.promec_engine) as session:
            service_order_repository = ServiceOrderRepository(session)
            service_orders: list[
                ServiceOrder
            ] = await service_order_repository.find_service_orders_by_order_type(
                order_type="TJ",
                period=period,
                include_detail=True,
            )

            logger.info(
                f"Cantidad de registros encontrados: {len(service_orders)} en el periodo {period}"
            )

            for service_order in service_orders:
                print(service_order)
                logger.info(
                    f"Detalles encontrados: {len(service_order.detail)} de la O/S: {service_order.id}"
                )
                for detail in service_order.detail:
                    print(detail)
