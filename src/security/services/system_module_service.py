from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import (
    SYSTEM_MODULE_NOT_FOUND_FAILURE,
)
from src.security.models import ModuloSistema
from src.security.repositories import ModuloSistemaRepository
from src.security.schemas import (
    SystemModuleCreateSchema,
    SystemModuleFilterParams,
    SystemModuleListSchema,
    SystemModuleSchema,
)


class SystemModuleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db
        self.repository: ModuloSistemaRepository = ModuloSistemaRepository(db)

    async def read_system_modules(
        self,
        filter_params: SystemModuleFilterParams,
    ) -> Result[SystemModuleListSchema, CustomException]:
        system_modules: list[ModuloSistema] = await self.repository.find_system_modules(
            **filter_params.model_dump()
        )

        return Success(SystemModuleListSchema(system_modules=system_modules))

    async def _read_system_module(
        self, system_module_id: int
    ) -> Result[ModuloSistema, CustomException]:
        system_module: ModuloSistema = await self.repository.find_system_module_by_id(
            id=system_module_id
        )

        if system_module is None:
            return SYSTEM_MODULE_NOT_FOUND_FAILURE

        return Success(system_module)

    async def read_system_module(
        self, system_module_id: int
    ) -> Result[SystemModuleSchema, CustomException]:
        system_module: Success = await self._read_system_module(system_module_id)

        if system_module.is_failure:
            return system_module

        return Success(SystemModuleSchema.model_validate(system_module.value))

    async def create_system_module(
        self, form: SystemModuleCreateSchema
    ) -> Result[SystemModuleSchema, CustomException]:
        system_module: ModuloSistema = ModuloSistema(**form.model_dump())

        await self.repository.save(system_module, flush=True)

        return Success(SystemModuleSchema.model_validate(system_module))
