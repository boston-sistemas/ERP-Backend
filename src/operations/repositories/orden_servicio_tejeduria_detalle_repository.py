from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import OrdenServicioTejeduriaDetalle


class OrdenServicioTejeduriaDetalleRepository(
    BaseRepository[OrdenServicioTejeduriaDetalle]
):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenServicioTejeduriaDetalle, db, flush)

    async def find_suborden(
        self, filter: BinaryExpression
    ) -> OrdenServicioTejeduriaDetalle | None:
        suborden = await self.find(filter=filter)

        return suborden
