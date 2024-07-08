from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import AccesoFailures
from src.security.models import Acceso
from src.security.repositories import AccesoRepository


class AccesoService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = AccesoRepository(db)

    async def read_acceso(self, acceso_id: int) -> Result[Acceso, CustomException]:
        acceso = await self.repository.find_by_id(acceso_id)

        if acceso is not None:
            return Success(acceso)

        return AccesoFailures.ACCESO_NOT_FOUND_FAILURE

    async def read_accesos(self) -> list[Acceso]:
        return await self.repository.find_all()
