from loguru import logger
from models_postgres import (
    ServiceOrderPCP,
    ServiceOrderPCPDetail,
)
from sqlalchemy import (
    Engine,
    and_,
    or_,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    joinedload,
)

from src.core.constants import MECSA_COMPANY_CODE
from src.operations.constants import UNSTARTED_SERVICE_ORDER_ID
from src.operations.models import (
    Movement,
    MovementYarnOCHeavy,
    ServiceOrder,
    ServiceOrderDetail,
)
from src.operations.repositories import (
    YarnPurchaseEntryRepository,
    YarnWeavingDispatchRepository,
)


class DataParser:
    def __init__(self, promec_engine: Engine, pcp_engine) -> None:
        self.promec_engine = promec_engine
        self.pcp_engine = pcp_engine

    async def parse_yarn_purchase_entry_heavies(self) -> None:
        async with AsyncSession(bind=self.promec_engine) as session:
            result = await session.execute(
                update(MovementYarnOCHeavy)
                .where(MovementYarnOCHeavy.item_number == None)
                .values(item_number=1)
            )
            updated_count = result.rowcount
            await session.commit()

            logger.info(f"Registros actualizados: {updated_count}")

    async def parse_period_yarn_purchase_entries(self, period: int) -> None:
        async with AsyncSession(bind=self.promec_engine) as session:
            yarn_repository = YarnPurchaseEntryRepository(session)
            yarn_purchase_entries: list[
                Movement
            ] = await yarn_repository.find_yarn_purchase_entries(
                period=period, include_detail=True, apply_unique=True
            )

            logger.info(
                f"Cantidad de registros encontrados: {len(yarn_purchase_entries)}"
            )

            for entry in yarn_purchase_entries:
                for detail in entry.detail:
                    if detail.detail_aux:
                        if detail.detail_aux.supplier_batch != "":
                            entry.supplier_batch = detail.detail_aux.supplier_batch
                            entry.mecsa_batch = detail.detail_aux.mecsa_batch
                            detail.supplier_batch = entry.supplier_batch

                    if detail.detail_heavy:
                        detail.is_weighted = True

                    guide_gross_weight = 0

                    for heavy in detail.detail_heavy:
                        heavy.supplier_batch = entry.supplier_batch
                        heavy.mecsa_batch = entry.mecsa_batch
                        heavy.period = entry.period
                        guide_gross_weight += heavy.gross_weight

                    detail.guide_gross_weight = round(guide_gross_weight, 6)

            try:
                for entry in yarn_purchase_entries:
                    logger.info(f"Actualizando registro {entry.document_number}")
                    session.add(entry)
                    print(entry)
                    for detail in entry.detail:
                        print(detail)
                        session.add(detail)

                        for heavy in detail.detail_heavy:
                            session.add(heavy)
                            if heavy.ingress_number != entry.document_number:
                                logger.error(
                                    f"El número de ingreso {heavy.ingress_number} no coincide con el número de documento {entry.document_number}"
                                )
                            else:
                                print(heavy)

                    await session.flush()
                    print("\n\n\n")

                await session.commit()
                logger.info("Todos los registros han sido actualizados correctamente")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error al actualizar registros: {str(e)}")

    async def parse_period_service_order_weaving(self, period: int) -> None:
        service_orders_detail: list[ServiceOrderDetail] = []

        async with AsyncSession(bind=self.pcp_engine) as session:
            stmt = (
                select(ServiceOrderPCP)
                .filter(ServiceOrderPCP.period == str(period))
                .options(joinedload(ServiceOrderPCP.detail))
            )

            result = await session.execute(stmt)
            service_orders_result: list[ServiceOrderPCP] = (
                result.unique().scalars().all()
            )

            for order in service_orders_result:
                for detail in order.detail:
                    print(detail)
                    service_order_detail_result: ServiceOrderDetail = (
                        ServiceOrderDetail(
                            company_code=MECSA_COMPANY_CODE,
                            order_id=order.id,
                            order_type="TJ",
                            product_id=detail.product_id,
                            quantity_ordered=detail.quantity_ordered,
                            quantity_supplied=0,
                            price=0,
                            status_param_id=UNSTARTED_SERVICE_ORDER_ID,
                        )
                    )
                    service_orders_detail.append(service_order_detail_result)

                print("\n\n\n")

        async with AsyncSession(bind=self.promec_engine) as session:
            for detail in service_orders_detail:
                logger.info(
                    f"Actualizando el detalle del registro {order.id} con tejido {detail.product_id}"
                )
                print(detail)
                session.add(detail)

                try:
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    logger.error(
                        f"Error al actualizar el detalle del registro {order.id} con tejido {detail.product_id}: {str(e)}"
                    )
                print("\n\n\n")

    async def parse_period_yarn_weaving_dispatches(self, period: int) -> None:
        async with AsyncSession(bind=self.promec_engine) as session:
            yarn_repository = YarnWeavingDispatchRepository(session)
            yarn_weaving_dispatches: list[
                Movement
            ] = await yarn_repository.find_yarn_weaving_dispatches(
                period=period, include_detail=True, apply_unique=True
            )

            logger.info(
                f"Cantidad de registros encontrados: {len(yarn_weaving_dispatches)}"
            )

            for entry in yarn_weaving_dispatches:
                print(entry)
                for detail in entry.detail:
                    print(detail)
                    if detail.detail_aux:
                        print(detail.detail_aux)
