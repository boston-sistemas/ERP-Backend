from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import (
    CustomException,
)
from src.core.result import Result, Success
from src.security.failures import RolFailures
from src.security.models import Rol, RolAcceso
from src.security.repositories import (
    RolAccesoRepository,
    RolRepository,
)
from src.security.schemas import (
    RolCreateSchema,
    RolCreateWithAccesosSchema,
    RolUpdateSchema,
)

from .acceso_service import AccesoService


class RolService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = RolRepository(db)
        self.acceso_service = AccesoService(db)
        self.rol_acceso_repository = RolAccesoRepository(db)

    async def read_rol(
        self, rol_id: int, include_accesos: bool = False
    ) -> Result[Rol, CustomException]:
        rol = await self.repository.find_rol(
            Rol.rol_id == rol_id, include_accesos=include_accesos
        )

        if rol is not None:
            return Success(rol)

        return RolFailures.ROL_NOT_FOUND_FAILURE

    async def read_roles(self) -> list[Rol]:
        return await self.repository.find_all(
            options=(self.repository.include_accesos(),), apply_unique=True
        )

    async def validate_rol_data(
        self, nombre: str | None = None
    ) -> Result[None, CustomException]:
        nombre_exists = nombre and (await self.repository.find(Rol.nombre == nombre))

        if nombre_exists:
            return RolFailures.ROL_NAME_ALREADY_EXISTS_FAILURE(nombre)

        return Success(None)

    async def create_rol(
        self, rol_data: RolCreateSchema | dict
    ) -> Result[None, CustomException]:
        rol_dict = rol_data if isinstance(rol_data, dict) else rol_data.model_dump()

        validation_result = await self.validate_rol_data(rol_dict["nombre"])
        if validation_result.is_failure:
            return validation_result

        rol = Rol(**rol_dict)
        await self.repository.save(rol)

        return Success(rol)

    def _create_rol_with_accesos_in_single_commit(func):
        async def wrapper(self, *args, **kwargs):
            self.repository.commit = False
            self.repository.flush = True
            # TODO: reiniciar los valores?
            return await func(self, *args, **kwargs)

        return wrapper

    @_create_rol_with_accesos_in_single_commit
    async def create_rol_with_accesos(
        self, rol_data: RolCreateWithAccesosSchema
    ) -> Result[None, CustomException]:
        creation_result = await self.create_rol(
            rol_data.model_dump(exclude={"acceso_ids"})
        )
        if creation_result.is_failure:
            return creation_result

        rol: Rol = creation_result.value
        add_accesos_result = await self._add_accesos_to_rol_instance(
            rol=rol, acceso_ids=rol_data.acceso_ids
        )
        if add_accesos_result.is_failure:
            return RolFailures.ACCESO_NOT_FOUND_WHEN_CREATING_FAILURE

        return Success(None)

    async def update_rol(
        self, id: int, update_data: RolUpdateSchema
    ) -> Result[None, CustomException]:
        rol_result = await self.read_rol(id)
        if rol_result.is_failure:
            return rol_result

        validation_result = await self.validate_rol_data(update_data.nombre)
        if validation_result.is_failure:
            return validation_result

        rol: Rol = rol_result.value

        for key, value in update_data.model_dump(exclude_none=True).items():
            setattr(rol, key, value)

        await self.repository.save(rol)

        return Success(None)

    async def delete_rol(self, id: int) -> Result[None, CustomException]:
        rol_result = await self.read_rol(id)
        if rol_result.is_failure:
            return rol_result

        user: Rol = rol_result.value
        await self.repository.delete(user)

        return Success(None)

    async def has_acceso(
        self, rol_id: int, acceso_id: int
    ) -> Result[RolAcceso, CustomException]:
        has_acceso, rol_acceso = await self.rol_acceso_repository.exists(
            (RolAcceso.rol_id == rol_id) & (RolAcceso.acceso_id == acceso_id)
        )

        if has_acceso:
            return Success(rol_acceso)

        return RolFailures.ROL_ACCESO_NOT_FOUND_FAILURE

    async def _add_accesos_to_rol_instance(
        self, rol: Rol, acceso_ids: list[int]
    ) -> Result[None, CustomException]:
        rol_id: int = rol.rol_id

        accesos_to_add = []
        for acceso_id in set(acceso_ids):
            acceso_result = await self.acceso_service.read_acceso(acceso_id)
            if acceso_result.is_failure:
                return RolFailures.ACCESO_NOT_FOUND_WHEN_ADDING_FAILURE

            has_acceso_validation = await self.has_acceso(rol_id, acceso_id)
            if has_acceso_validation.is_success:
                return RolFailures.ROL_HAS_ACCESO_WHEN_ADDING_FAILURE

            acceso = acceso_result.value
            accesos_to_add.append(RolAcceso(rol_id=rol_id, acceso_id=acceso.acceso_id))

        await self.rol_acceso_repository.save_all(accesos_to_add)

        return Success(None)

    async def add_accesos_to_rol(
        self, rol_id: int, acceso_ids: list[int]
    ) -> Result[None, CustomException]:
        rol_result = await self.read_rol(rol_id)
        if rol_result.is_failure:
            return rol_result

        return await self._add_accesos_to_rol_instance(
            rol=rol_result.value, acceso_ids=acceso_ids
        )

    async def delete_accesos_from_rol(
        self, rol_id: int, acceso_ids: list[int]
    ) -> Result[None, CustomException]:
        rol_result = await self.read_rol(rol_id)
        if rol_result.is_failure:
            return rol_result

        accesos_to_delete = []
        for acceso_id in set(acceso_ids):
            acceso_result = await self.acceso_service.read_acceso(acceso_id)
            if acceso_result.is_failure:
                return RolFailures.ACCESO_NOT_FOUND_WHEN_DELETING_FAILURE

            has_acceso_validation = await self.has_acceso(rol_id, acceso_id)
            if has_acceso_validation.is_failure:
                return RolFailures.ROL_MISSING_ACCESO_WHEN_DELETING_FAILURE

            accesos_to_delete.append(has_acceso_validation.value)

        await self.rol_acceso_repository.delete_all(accesos_to_delete)

        return Success(None)
