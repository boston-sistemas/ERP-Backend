from sqlalchemy.ext.asyncio import AsyncSession

from src.operations.repositories import OrdenCompraRepository
from src.core.exceptions import CustomException
from src.core.result import Result, Success

from src.operations.models import OrdenCompra

class OrdenCompraService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenCompraRepository(db)

    async def read_ordenes_yarn(
        self,
        include_detalle: bool = False,
    ) -> list[OrdenCompra]:
        return await self.repository.find_ordenes_yarn(
            include_detalle=include_detalle
        )
