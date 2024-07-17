from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.operations.models import EspecialidadEmpresa


class EspecialidadEmpresaRepository(BaseRepository[EspecialidadEmpresa]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(EspecialidadEmpresa, db, flush)

    @staticmethod
    def include_proveedores() -> Load:
        return joinedload(EspecialidadEmpresa.proveedores)

    async def find_especialidad(
        self, filter: BinaryExpression, include_proveedores: bool = False
    ) -> EspecialidadEmpresa | None:
        options: list[Load] = []

        if include_proveedores:
            options.append(self.include_proveedores())

        especialidad = await self.find(filter, options=options)

        return especialidad
