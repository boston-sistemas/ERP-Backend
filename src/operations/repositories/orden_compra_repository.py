from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BinaryExpression, and_, func
from sqlalchemy.orm import (
    joinedload,
    aliased
)
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import OrdenCompra, OrdenCompraDetalle, Hilado


class OrdenCompraRepository(BaseRepository[OrdenCompra]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenCompra, db, flush)

    @staticmethod
    def include_detalle() -> Load:
        return joinedload(OrdenCompra.detalle)

    @staticmethod
    def include_detalle_hilados() -> Load:
        return joinedload(OrdenCompra.detalle).joinedload(OrdenCompraDetalle.hilado)

    async def find_ordenes_hilado(
        self,
        # filter: BinaryExpression = None,
        include_detalle: bool = False,
    ) -> list[OrdenCompra]:
        options: list[Load] = []
        joins: list[tuple] = []

        if include_detalle:
            options.append(self.include_detalle())

        detalle_alias = aliased(OrdenCompraDetalle)
        # hilado_alias = aliased(Hilado)

        # joins.append((detalle_alias, and_(
        #     OrdenCompra.codcia == detalle_alias.codcia,
        #     OrdenCompra.purchase_order_type == detalle_alias.purchase_order_type,
        #     OrdenCompra.purchase_order_number == detalle_alias.purchase_order_number
        # )))

        # joins.append((hilado_alias, and_(
        #     detalle_alias.codcia == hilado_alias.codcia,
        #     detalle_alias.product_code == hilado_alias.yarn_code
        # )))

        filter = and_(
            OrdenCompra.codcia == '001',
            OrdenCompra.status_flag == 'P',
            func.locate('TITULO GRATUITO', OrdenCompra.payment_method) == 0,
            OrdenCompra.detalle.any(  # Filtra detalles
                and_(
                    OrdenCompraDetalle.hilado.has(  # Verifica la relación con hilado
                        and_(
                            Hilado.family_code == '03',
                            Hilado.subfamily_code == '09'
                        )
                    )
                )
            )
            # hilado_alias.family_code == '03',
            # hilado_alias.subfamily_code == '09'
        )

        ordenes = await self.find_all(
            filter=filter, joins=joins, options=options, apply_unique=True
        )

        print("asdasdsadsa")
        print("asdasdsadsa")
        print("asdasdsadsa")
        print("asdasdsadsa")
        print("asdasdsadsa")
        print("asdasdsadsa")
        print("asdasdsadsa")

        return ordenes



