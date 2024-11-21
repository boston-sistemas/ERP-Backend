from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import OrdenCompra, OrdenCompraDetalle


class OrdenCompraRepository(BaseRepository[OrdenCompra]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenCompra, db, flush)

    @staticmethod
    def include_detalle() -> Load:
        return joinedload(OrdenCompra.detalles)

    # @staticmethod
    # def include_detalle_hilados() -> Load:
    #     return joinedload(OrdenCompra.detalles).joinedload(OrdenCompraDetalle.hilado)
