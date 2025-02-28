from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import AccesoFailures
from src.security.models import Acceso
from src.security.repositories import AccesoRepository
from src.security.schemas import (
    AccesoSchema,
    AccessCreateSchema,
    SystemModuleSchema,
)

from .system_module_service import SystemModuleService


class AccesoService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = AccesoRepository(db)
        self.system_module_service = SystemModuleService(db=db)

    async def _read_access(self, access_id: int) -> Result[Acceso, CustomException]:
        access: Acceso = await self.repository.find_by_id(access_id)

        if access is None:
            return AccesoFailures.ACCESO_NOT_FOUND_FAILURE

        return Success(access)

    async def read_acceso(
        self, acceso_id: int
    ) -> Result[AccesoSchema, CustomException]:
        access: Success = await self._read_access(access_id=acceso_id)

        if access.is_failure:
            return access

        return Success(AccesoSchema.model_validate(access.value))

    async def read_accesos(self) -> list[Acceso]:
        return await self.repository.find_all()

    async def _validate_access_data(
        self,
        data: AccessCreateSchema,
    ) -> Result[None, CustomException]:
        system_module_result: Success = (
            await self.system_module_service.read_system_module(
                system_module_id=data.system_module_id
            )
        )

        if system_module_result.is_failure:
            return system_module_result

        system_module: SystemModuleSchema = system_module_result.value

        if not system_module.is_active:
            return AccesoFailures.ACCESS_SYSTEM_MODULE_ANULLED_FAILURE

        return Success(None)

    async def create_access(
        self,
        form: AccessCreateSchema,
    ) -> Result[AccesoSchema, CustomException]:
        validation_result: Success = await self._validate_access_data(data=form)

        if validation_result.is_failure:
            return validation_result

        access: Acceso = Acceso(
            nombre=form.name,
            scope=form.scope,
            modulo_id=form.system_module_id,
            view_path=form.view_path,
            image_path=form.image_path,
            description=form.description,
            is_active=form.is_active,
        )

        await self.repository.save(access, flush=True)

        return Success(AccesoSchema.model_validate(access))
