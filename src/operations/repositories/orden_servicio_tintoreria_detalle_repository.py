from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import OrdenServicioTintoreriaDetalle


class OrdenServicioTintoreriaDetalleRepository(
    BaseRepository[OrdenServicioTintoreriaDetalle]
):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(OrdenServicioTintoreriaDetalle, db, commit)
