from sqlalchemy.ext.asyncio import AsyncSession

from src.core.result import Result, Success
from src.operations.models import OrdenServicioTintoreriaDetalle
from src.operations.repositories import OrdenServicioTintoreriaDetalleRepository
from src.operations.schemas import OrdenServicioTintoreriaDetalleCreateSchema


class OrdenServicioTintoreriaDetalleService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenServicioTintoreriaDetalleRepository(db)

    async def create_subordenes(
        self, subordenes: list[OrdenServicioTintoreriaDetalleCreateSchema]
    ) -> Result[None, None]:
        instances = [
            OrdenServicioTintoreriaDetalle(**suborden.model_dump())
            for suborden in subordenes
        ]
        await self.repository.save_all(instances)

        return Success(None)
