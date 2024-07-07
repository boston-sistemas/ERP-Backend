from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import (
    CustomException,
    DuplicateValueException,
    NotFoundException,
)
from src.core.result import Failure, Result, Success
from src.security.models import Rol, RolAcceso
from src.security.repositories import (
    AccesoRepository,
    RolAccesoRepository,
    RolRepository,
)
from src.security.schemas import RolCreateSchema, RolUpdateSchema


class RolService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = RolRepository(db)
        self.acceso_repository = AccesoRepository(db)
        self.rol_acceso_repository = RolAccesoRepository(db)

    async def read_rol(
        self, id: int, include_accesos: bool = False
    ) -> Result[Rol, CustomException]:
        rol = await self.repository.find_rol(
            Rol.rol_id == id, include_accesos=include_accesos
        )

        if rol is not None:
            return Success(rol)

        return Failure(NotFoundException("Rol no encontrado"))

    async def read_roles(self) -> list[Rol]:
        return await self.repository.find_all(
            options=(self.repository.include_accesos(),), apply_unique=True
        )

    async def validate_rol_data(
        self, nombre: str | None = None
    ) -> Result[None, CustomException]:
        nombre_exists = nombre and (await self.repository.find(Rol.nombre == nombre))

        if nombre_exists:
            return Failure(DuplicateValueException(f"Rol {nombre} ya existe"))

        return Success(None)

    async def create_rol(
        self, rol_data: RolCreateSchema
    ) -> Result[None, CustomException]:
        validation_result = await self.validate_rol_data(rol_data.nombre)
        if validation_result.is_failure:
            return validation_result

        rol = Rol(**rol_data.model_dump(exclude={"acceso_ids"}))

        if rol_data.acceso_ids:
            for acceso_id in set(rol_data.acceso_ids):
                acceso = await self.acceso_repository.find_by_id(acceso_id)
                if acceso is None:
                    return Failure(
                        NotFoundException("Acceso no encontrado. Rol no creado")
                    )

                rol.accesos.append(acceso)

        await self.repository.save(rol)

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

    @staticmethod
    def has_acceso_instance(rol: Rol, acceso_id: int) -> bool:
        return any(acceso.acceso_id == acceso_id for acceso in rol.accesos)

    async def has_acceso(
        self, rol_id: int, acceso_id: int
    ) -> Result[RolAcceso, CustomException]:
        has_acceso, rol_acceso = await self.rol_acceso_repository.exists(
            (RolAcceso.rol_id == rol_id) & (RolAcceso.acceso_id == acceso_id)
        )

        if has_acceso:
            return Success(rol_acceso)

        return Failure(NotFoundException("El rol no cuenta con el acceso"))

    async def add_accesos_to_rol(
        self, id: int, acceso_ids: list[int]
    ) -> Result[None, CustomException]:
        rol_result = await self.read_rol(id)
        if rol_result.is_failure:
            return rol_result

        accesos_to_add = []
        for acceso_id in set(acceso_ids):
            acceso = await self.acceso_repository.find_by_id(acceso_id)
            if acceso is None:
                return Failure(
                    NotFoundException(
                        "Acceso no encontrado. No se añadieron los accesos especificados"
                    )
                )

            has_acceso_validation = await self.has_acceso(id, acceso_id)
            if has_acceso_validation.is_success:
                return Failure(
                    DuplicateValueException(
                        "El rol ya cuenta con el acceso. No se añadieron los accesos especificados"
                    )
                )

            accesos_to_add.append(RolAcceso(rol_id=id, acceso_id=acceso.acceso_id))

        await self.rol_acceso_repository.save_all(accesos_to_add)

        return Success(None)

    async def delete_accesos_from_rol(
        self, id: int, acceso_ids: list[int]
    ) -> Result[None, CustomException]:
        rol_result = await self.read_rol(id)
        if rol_result.is_failure:
            return rol_result

        accesos_to_delete = []
        for acceso_id in set(acceso_ids):
            acceso = await self.acceso_repository.find_by_id(acceso_id)
            if acceso is None:
                return Failure(
                    NotFoundException(
                        "Acceso no encontrado. No se añadieron los accesos especificados"
                    )
                )

            has_acceso_validation = await self.has_acceso(id, acceso_id)
            if has_acceso_validation.is_failure:
                return Failure(
                    DuplicateValueException(
                        "El rol no cuenta con el acceso. No se eliminaron los accesos especificados"
                    )
                )

            accesos_to_delete.append(has_acceso_validation.value)

        await self.acceso_repository.delete_all(accesos_to_delete)

        return Success(None)
