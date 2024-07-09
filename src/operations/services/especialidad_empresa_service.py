from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import EspecialidadEmpresaFailures
from src.operations.models import EspecialidadEmpresa
from src.operations.repositories import EspecialidadEmpresaRepository


class EspecialidadEmpresaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = EspecialidadEmpresaRepository(db)

    async def read_especialidad_by_nombre(
        self, nombre: str, include_proveedores: bool = False
    ) -> Result[EspecialidadEmpresa, CustomException]:
        especialidad = self.repository.find_especialidad(
            EspecialidadEmpresa.nombre == nombre,
            include_proveedores=include_proveedores,
        )
        if especialidad is not None:
            return Success(especialidad)

        return EspecialidadEmpresaFailures.ESPECIALIDAD_NOT_FOUND_FAILURE
