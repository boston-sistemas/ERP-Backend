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
from sqlalchemy.orm import joinedload, load_only

from src.core.constants import MECSA_COMPANY_CODE
from src.operations.constants import (
    DISPATCH_MOVEMENT_TYPE,
    UNSTARTED_SERVICE_ORDER_ID,
    YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
    YARN_WEAVING_DISPATCH_STORAGE_CODE,
)
from src.operations.models import (
    FabricWarehouse,
    InventoryItem,
    Movement,
    MovementDetail,
    MovementYarnOCHeavy,
    ServiceOrder,
    ServiceOrderDetail,
    ServiceOrderSupplyDetail,
)
from src.operations.repositories import (
    ServiceOrderRepository,
    YarnPurchaseEntryRepository,
    YarnWeavingDispatchRepository,
)
from src.operations.services import FabricService


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

    async def parse_period_service_orders_supply_item_number(self, period: int) -> None:
        yarn_weaving_dispatches_detail: list[MovementDetail] = []
        async with AsyncSession(
            bind=self.promec_engine,
            expire_on_commit=False,
        ) as session:
            stmt = select(MovementDetail).where(
                (MovementDetail.company_code == MECSA_COMPANY_CODE)
                & (MovementDetail.storage_code == YARN_WEAVING_DISPATCH_STORAGE_CODE)
                & (MovementDetail.movement_type == DISPATCH_MOVEMENT_TYPE)
                & (MovementDetail.movement_code == YARN_WEAVING_DISPATCH_MOVEMENT_CODE)
                & (MovementDetail.document_code == YARN_WEAVING_DISPATCH_DOCUMENT_CODE)
                & (MovementDetail.period == period)
                & (MovementDetail.item_number_supply == None)
            )

            result = await session.execute(stmt)
            yarn_weaving_dispatches_detail: list[MovementDetail] = (
                result.unique().scalars().all()
            )

            logger.info(
                f"Cantidad de registros encontrados: {len(yarn_weaving_dispatches_detail)}"
            )

            for detail in yarn_weaving_dispatches_detail:
                detail.item_number_supply: int = 1
                item_number: int = detail.item_number
                service_order_id: str = detail.nroreq
                item_number_supply: int = detail.item_number_supply
                product_code: str = detail.product_code

                stmt = (
                    update(ServiceOrderSupplyDetail)
                    .where(
                        (ServiceOrderSupplyDetail.company_code == MECSA_COMPANY_CODE)
                        & (
                            ServiceOrderSupplyDetail.reference_number
                            == service_order_id
                        )
                        & (ServiceOrderSupplyDetail.product_code1 == product_code)
                        & (ServiceOrderSupplyDetail.item_number == None)
                    )
                    .values(item_number=item_number_supply)
                )

                result = await session.execute(stmt)
                updated_count = result.rowcount if result else 0

                if updated_count > 1:
                    logger.error(
                        f"Se han actualizado más de un registro para el número de referencia {service_order_id} y el código de producto {product_code}"
                    )

                try:
                    session.add(detail)
                    await session.commit()
                    logger.info(
                        f"Se ha actualizado el número de ítem {item_number_supply} para el número de referencia {service_order_id} con el código de producto {product_code} y el número de item del detalle {item_number}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error al actualizar el número de ítem {item_number_supply} para el número de referencia {service_order_id} con el código de producto {product_code} y el número de item del detalle {item_number}: {str(e)}"
                    )
                    await session.rollback()

    async def parse_period_service_orders_weaving_from_pcp(self, period: int) -> None:
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
                print(order)
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
                    f"Actualizando el detalle del registro {detail.order_id} con tejido {detail.product_id}"
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

    async def _find_service_order_weaving_detail_by_product_id(
        self,
        details: list[ServiceOrderDetail],
        product_id: str,
    ) -> ServiceOrderDetail:
        for detail in details:
            # logger.info(f"Comparando {detail.product_id[:8]} con {product_id[:8]}")
            # logger.info(f"Comparando {detail.product_id} con {product_id}")
            # logger.info(f"{len(product_id)}")
            print(f"Comparando {detail.product_id[:8]} con {product_id[:8]}")
            print(f"Comparando {detail.product_id} con {product_id}")
            print(f"{len(product_id)}")
            if len(detail.product_id) == 8:
                if detail.product_id[:8] == product_id[:8]:
                    return detail
            else:
                if detail.product_id == product_id:
                    return detail
        return None

    async def _find_service_order_weaving_detail_by_product_id_with_color(
        self,
        details: list[ServiceOrderDetail],
        product_id: str,
    ) -> ServiceOrderDetail:
        for detail in details:
            # logger.info(f"Comparando {detail.product_id} con {product_id}")
            # logger.info(f"{detail.product_id == product_id}")
            if detail.product_id == product_id:
                # logger.info(f"Detalle encontrado: {detail.product_id}")
                return detail

        return None

    async def parse_period_service_orders_weaving(self, period: int) -> None:
        async with AsyncSession(
            bind=self.promec_engine,
            expire_on_commit=False,
        ) as session:
            service_order_repository = ServiceOrderRepository(session)
            service_orders: list[
                ServiceOrder
            ] = await service_order_repository.find_service_orders_by_order_type(
                order_type="TJ", period=period, include_detail=True, apply_unique=True
            )

            logger.info(f"Cantidad de registros encontrados: {len(service_orders)}")
            for order in service_orders:
                logger.info(f"Orden encontrada: {order.id}")
                print(order)

                stmt = (
                    select(FabricWarehouse)
                    .options(
                        load_only(
                            FabricWarehouse.product_id, FabricWarehouse.service_order_id
                        )
                    )
                    .where(
                        and_(
                            FabricWarehouse.company_code == MECSA_COMPANY_CODE,
                            FabricWarehouse.service_order_id.like(f"%{order.id}%"),
                            FabricWarehouse.document_code == "P/I",
                        )
                    )
                )

                result = await session.execute(stmt)
                fabric_warehouse: list[FabricWarehouse] = (
                    result.unique().scalars().all()
                )
                product_ids: set[str] = {row.product_id for row in fabric_warehouse}

                service_orders_ingress: dict[str, str] = {}

                for fabric in fabric_warehouse:
                    service_order_id = fabric.service_order_id.split(",")
                    for so_id in service_order_id:
                        if so_id != order.id:
                            if fabric.product_id in service_orders_ingress:
                                service_orders_ingress[fabric.product_id].append(so_id)
                            else:
                                service_orders_ingress[fabric.product_id] = [so_id]

                for key, value in service_orders_ingress.items():
                    service_orders_ingress[key] = set(value)
                    service_orders_ingress[key] = list(service_orders_ingress[key])

                logger.info(f"Productos encontrados: {len(product_ids)}")
                print(f"Productos encontrados: {len(product_ids)}")
                print(product_ids, "\n")

                print(f"O/S encontradas: {len(service_orders_ingress)}")
                print(service_orders_ingress, "\n")

                product_ids_os: set[str] = set(
                    [detail.product_id[:8] for detail in order.detail]
                )

                for product_os in product_ids_os:
                    if not any(product_os[:8] == pid[:8] for pid in product_ids):
                        logger.error(
                            f"Producto no encontrado en los registros de ingreso: {product_os} O/S {order.id}"
                        )
                        print(
                            f"Producto no encontrado en los registros de ingreso: {product_os} O/S {order.id}"
                        )

                for product_id in product_ids:
                    detail: ServiceOrderDetail = (
                        await self._find_service_order_weaving_detail_by_product_id(
                            order.detail, product_id
                        )
                    )

                    if not detail:
                        service_order_detail_result: ServiceOrderDetail = (
                            ServiceOrderDetail(
                                company_code=MECSA_COMPANY_CODE,
                                order_id=order.id,
                                order_type="TJ",
                                product_id=product_id,
                                quantity_ordered=-1,
                                quantity_supplied=-1,
                                price=0,
                                status_param_id=UNSTARTED_SERVICE_ORDER_ID,
                            )
                        )
                        logger.error(
                            f"Detalle no encontrado para el producto {product_id} de la orden {order.id}"
                        )
                        print(
                            f"Detalle no encontrado para el producto {product_id} de la orden {order.id}"
                        )
                        order.detail.append(service_order_detail_result)

                        detail = service_order_detail_result

                    else:
                        print(
                            f"Detalle encontrado para el producto {product_id} de la orden {order.id} del producto {detail.product_id}"
                        )
                        detail.product_id = product_id

                    if order.id[:3] == "LYC":
                        detail_note = ";".join(service_orders_ingress[product_id]) + "|"
                        # print(detail_note)
                        detail.detail_note = detail_note

                    try:
                        session.add(detail)
                        await session.commit()
                    except Exception as e:
                        await session.rollback()
                        logger.error(
                            f"Error al actualizar el detalle del registro {order.id} con tejido {detail.product_id}: {str(e)}"
                        )
                        print(
                            f"Error al actualizar el detalle del registro {order.id} con tejido {detail.product_id}: {str(e)}"
                        )

                logger.info(
                    f"Detalles encontrados: {len(order.detail)} de la orden {order.id}"
                )
                for detail in order.detail:
                    print(detail)
                print("\n\n\n")

    async def parse_period_service_orders_weaving_stocks(self, period: int) -> None:
        async with AsyncSession(
            bind=self.promec_engine,
            expire_on_commit=False,
        ) as session:
            service_order_repository = ServiceOrderRepository(session)
            service_orders: list[
                ServiceOrder
            ] = await service_order_repository.find_service_orders_by_order_type(
                order_type="TJ", period=period, include_detail=True, apply_unique=True
            )

            logger.info(f"Cantidad de registros encontrados: {len(service_orders)}")

            for order in service_orders:
                logger.info(f"Orden encontrada: {order.id}")
                # print(order)

                if order.id[:3] == "LYC":
                    continue

                stmt = select(
                    FabricWarehouse.product_id, FabricWarehouse.guide_net_weight
                ).where(
                    and_(
                        FabricWarehouse.company_code == MECSA_COMPANY_CODE,
                        FabricWarehouse.service_order_id.like(f"%{order.id}%"),
                        FabricWarehouse.document_code == "P/I",
                    )
                )

                result = await session.execute(stmt)
                product_ids = {}

                for product_id, guide_net_weight in result.all():
                    # print(product_id, guide_net_weight)
                    if product_id in product_ids:
                        product_ids[product_id] += round(guide_net_weight, 4)
                    else:
                        product_ids[product_id] = round(guide_net_weight, 4)

                product_ids = {k: round(v, 4) for k, v in product_ids.items()}

                product_ids = dict(
                    sorted(product_ids.items(), key=lambda item: item[1], reverse=False)
                )

                product_ids_os: dict[str, float] = {
                    detail.product_id: detail.quantity_ordered
                    for detail in order.detail
                    if detail.quantity_ordered > 0
                }
                product_ids_os = dict(
                    sorted(
                        product_ids_os.items(), key=lambda item: item[1], reverse=True
                    )
                )

                suma_total_ids = sum(product_ids.values())
                suma_total_ids_os = sum(product_ids_os.values())

                if suma_total_ids > suma_total_ids_os:
                    print(
                        f"La suma total de los productos encontrados es mayor a la suma total de los productos de la O/S {order.id}"
                    )
                    logger.error(
                        f"La suma total de los productos encontrados es mayor a la suma total de los productos de la O/S {order.id}"
                    )

                if product_ids_os:
                    max_key, max_value = next(iter(product_ids_os.items()))
                else:
                    max_key, max_value = 0, 0

                detail_result: ServiceOrderDetail = None
                other_detail: ServiceOrderDetail = None

                print("--->", order.id)

                for product in product_ids:
                    res = 0
                    detail_result = await self._find_service_order_weaving_detail_by_product_id_with_color(
                        details=order.detail,
                        product_id=product,
                    )
                    # logger.info(f"Detalle: {type(detail_result)}")
                    print("->", product, product_ids, product_ids_os)
                    print("-->", max_key, max_value)
                    if product in product_ids_os:
                        if product_ids[product] <= product_ids_os[product]:
                            detail_result.quantity_supplied = product_ids[product]
                        else:
                            res = round(
                                product_ids[product] - product_ids_os[product], 4
                            )
                            detail_result.quantity_ordered = product_ids[product]
                            detail_result.quantity_supplied = product_ids[product]
                    else:
                        res = product_ids[product]
                        detail_result.quantity_ordered = product_ids[product]
                        detail_result.quantity_supplied = product_ids[product]

                    if product_ids_os:
                        res_max = round(max_value - res, 4)
                        print(res_max, max_value, res)

                        if max_key in product_ids:
                            if res_max < product_ids[max_key]:
                                res_max = max_value - product_ids[max_key]
                                first_key = next(iter(product_ids_os))
                                del product_ids_os[first_key]
                                if product_ids_os:
                                    max_key, max_value = next(
                                        iter(product_ids_os.items())
                                    )
                                else:
                                    max_key, max_value = 0, 0
                            else:
                                product_ids_os[max_key] = res_max
                                max_key, max_value = next(iter(product_ids_os.items()))

                                other_detail = await self._find_service_order_weaving_detail_by_product_id_with_color(
                                    details=order.detail, product_id=max_key
                                )

                                other_detail.quantity_ordered = max_value

                        else:
                            product_ids_os[max_key] = res_max
                            max_key, max_value = next(iter(product_ids_os.items()))

                            other_detail = await self._find_service_order_weaving_detail_by_product_id_with_color(
                                details=order.detail, product_id=max_key
                            )

                            other_detail.quantity_ordered = max_value

                    print(detail_result)
                    try:
                        session.add(detail_result)

                        if other_detail:
                            session.add(other_detail)

                            other_detail = None
                        await session.commit()
                    except Exception as e:
                        await session.rollback()
                        logger.error(
                            f"Error al actualizar el detalle del registro {order.id} con tejido {detail_result.product_id}: {str(e)}"
                        )
                        print(
                            f"Error al actualizar el detalle del registro {order.id} con tejido {detail_result.product_id}: {str(e)}"
                        )

    async def parse_period_service_orders_weaving_stocks_lyc(self, period: int) -> None:
        async with AsyncSession(
            bind=self.promec_engine,
            expire_on_commit=False,
        ) as session:
            service_order_repository = ServiceOrderRepository(session)
            fabric_service = FabricService(promec_db=session, db=None)
            service_orders: list[
                ServiceOrder
            ] = await service_order_repository.find_service_orders_by_order_type(
                order_id="LYC",
                order_type="TJ",
                period=period,
                include_detail=True,
                apply_unique=True,
            )

            logger.info(f"Cantidad de registros LYC encontrados: {len(service_orders)}")
            for order in service_orders:
                logger.info(f"Orden LYC encontrada: {order.id}")

                for detail in order.detail:
                    fabric: InventoryItem = await fabric_service._read_fabric(
                        fabric_id=detail.product_id,
                        include_color=True,
                        include_recipe=True,
                    )
                    print(fabric.id)
                    print(fabric.fabric_recipe)

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
