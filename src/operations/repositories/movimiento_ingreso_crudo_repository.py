from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.operations.models import MovimientoIngresoCrudo


class MovimientoIngresoCrudoRepository(BaseRepository[MovimientoIngresoCrudo]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(MovimientoIngresoCrudo, db, flush)
