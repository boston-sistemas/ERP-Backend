from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import ProveedorFailures
from src.operations.models import Proveedor
from src.operations.repositories import ProveedorRepository

from .especialidad_empresa_service import EspecialidadEmpresaService


class ProveedorService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ProveedorRepository(db)
        self.especialidad_service = EspecialidadEmpresaService(db)

    async def read_proveedor(
        self, proveedor_id: str
    ) -> Result[Proveedor, CustomException]:
        proveedor = await self.repository.find(Proveedor.proveedor_id == proveedor_id)
        if proveedor is not None:
            return Success(proveedor)

        return ProveedorFailures.PROVEEDOR_NOT_FOUND_FAILURE

    async def read_proveedores_by_especialidad(
        self, especialidad: str
    ) -> Result[list[Proveedor], CustomException]:
        result = await self.especialidad_service.read_especialidad_by_nombre(
            nombre=especialidad, include_proveedores=True
        )
        if result.is_failure:
            return result

        proveedores = result.value.proveedores
        return Success(proveedores)
