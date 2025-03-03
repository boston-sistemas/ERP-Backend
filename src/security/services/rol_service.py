from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import transactional
from src.core.exceptions.http_exceptions import (
    CustomException,
)
from src.core.result import Result, Success
from src.security.failures import RolFailures
from src.security.models import Rol, RolAccesoOperation
from src.security.repositories import (
    RolAccesoOperationRepository,
    RolRepository,
)
from src.security.schemas import (
    AccesoCreateWithOperationSchema,
    AccesoSchema,
    RolCreateAccessWithOperationSchema,
    RolCreateSchema,
    RolCreateWithAccesosSchema,
    RolDeleteAccessWithOperationSchema,
    RolListSchema,
    RolSchema,
    RolUpdateSchema,
)

from .acceso_service import AccesoService
from .operation_service import OperationService


class RolService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = RolRepository(db)
        self.acceso_service = AccesoService(db)
        self.rol_acceso_operation_repository = RolAccesoOperationRepository(db)
        self.operation_service = OperationService(db=db)

    async def _read_rol(
        self, rol_id: int, include_access_operation: bool = False
    ) -> Result[Rol, CustomException]:
        rol: Rol = await self.repository.find_rol_by_id(
            rol_id=rol_id,
            include_access_operation=include_access_operation,
        )

        if rol is None:
            return RolFailures.ROL_NOT_FOUND_FAILURE

        return Success(rol)

    async def read_rol(
        self, rol_id: int, include_access_operation: bool = False
    ) -> Result[Rol, CustomException]:
        rol: Success = await self._read_rol(
            rol_id=rol_id, include_access_operation=include_access_operation
        )

        if rol.is_failure:
            return rol

        return Success(RolSchema.model_validate(rol.value))

    async def read_roles(
        self,
        include_access_operation: bool = False,
        include_inactive: bool = False,
    ) -> Result[RolListSchema, CustomException]:
        roles: list[Rol] = await self.repository.find_roles(
            include_inactive=include_inactive,
            include_access_operation=include_access_operation,
        )

        return Success(RolListSchema(roles=roles))

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
        await self.repository.save(rol, flush=True)

        return Success(rol)

    @transactional
    async def create_rol_with_accesos(
        self, rol_data: RolCreateWithAccesosSchema
    ) -> Result[None, CustomException]:
        creation_result = await self.create_rol(
            rol_data.model_dump(exclude={"accesses"})
        )
        if creation_result.is_failure:
            return creation_result

        rol: Rol = creation_result.value
        add_accesos_result = await self._add_accesses_operations_to_rol_instance(
            rol=rol, accesses=rol_data.accesses
        )
        if add_accesos_result.is_failure:
            return add_accesos_result

        rol_result: RolSchema = RolSchema.model_validate(rol)
        rol_result.access = add_accesos_result.value

        return Success(rol_result)

    async def update_rol(
        self, id: int, update_data: RolUpdateSchema
    ) -> Result[None, CustomException]:
        rol_result = await self._read_rol(rol_id=id)
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
        rol_result = await self._read_rol(rol_id=id)
        if rol_result.is_failure:
            return rol_result

        rol: Rol = rol_result.value

        rol.is_active = False
        await self.repository.save(rol)

        return Success(None)

    async def has_access_operation(
        self, rol_id: int, acceso_id: int, operation_id: int
    ) -> Result[RolAccesoOperation, CustomException]:
        has_acceso, rol_acceso = await self.rol_acceso_operation_repository.exists(
            (RolAccesoOperation.rol_id == rol_id)
            & (RolAccesoOperation.acceso_id == acceso_id)
            & (RolAccesoOperation.operation_id == operation_id)
        )

        if has_acceso:
            return Success(rol_acceso)

        return RolFailures.ROL_ACCESO_NOT_FOUND_FAILURE

    async def _add_accesses_operations_to_rol_instance(
        self, rol: Rol, accesses: list[AccesoCreateWithOperationSchema]
    ) -> Result[None, CustomException]:
        rol_id: int = rol.rol_id

        access_operation_to_scheme: list[AccesoSchema] = []
        access_operation_to_add = []
        for access in accesses:
            acceso_result = await self.acceso_service.read_acceso(
                access.acceso_id,
                include_operations=True,
            )

            if acceso_result.is_failure:
                return RolFailures.ACCESO_NOT_FOUND_WHEN_ADDING_FAILURE

            for operation in access.operation_ids:
                operation_id: int = operation

                operation_result = next(
                    (
                        access_operation
                        for access_operation in acceso_result.value.operations
                        if access_operation.operation_id == operation_id
                    ),
                    None,
                )

                if operation_result is None:
                    return RolFailures.ROL_ACCESS_NOT_ASSIGNED_OPERATION_FAILURE

                validation_result = await self.has_access_operation(
                    rol_id, access.acceso_id, operation_id
                )
                if validation_result.is_failure:
                    access_operation_to_add.append(
                        RolAccesoOperation(
                            rol_id=rol_id,
                            acceso_id=acceso_result.value.acceso_id,
                            operation_id=operation_id,
                        )
                    )
                acceso_result.value.role_operations.append(operation_result)
            acceso_result.value.operations = []
            access_operation_to_scheme.append(acceso_result.value)

        await self.rol_acceso_operation_repository.save_all(access_operation_to_add)

        return Success(access_operation_to_scheme)

    async def add_accesos_to_rol(
        self, rol_id: int, form: RolCreateAccessWithOperationSchema
    ) -> Result[None, CustomException]:
        rol_result = await self.read_rol(rol_id)
        if rol_result.is_failure:
            return rol_result

        rol: Rol = rol_result.value
        add_accesos_result = await self._add_accesses_operations_to_rol_instance(
            rol=rol, accesses=form.accesses
        )
        if add_accesos_result.is_failure:
            return add_accesos_result

        rol_result: RolSchema = RolSchema.model_validate(rol)
        rol_result.access = add_accesos_result.value

        return Success(rol_result)

    async def delete_accesos_from_rol(
        self, rol_id: int, form: RolDeleteAccessWithOperationSchema
    ) -> Result[None, CustomException]:
        rol_result = await self._read_rol(rol_id, include_access_operation=True)
        if rol_result.is_failure:
            return rol_result

        rol: Rol = rol_result.value

        access_operation_to_delete = []
        for access in form.accesses:
            access_id: int = access.acceso_id
            acceso_result = await self.acceso_service.read_acceso(
                acceso_id=access_id,
                include_operations=True,
            )
            if acceso_result.is_failure:
                return RolFailures.ACCESO_NOT_FOUND_WHEN_DELETING_FAILURE

            for operation in access.operation_ids:
                operation_id: int = operation

                operation_result = await self.operation_service.read_operation(
                    operation_id
                )
                if operation_result.is_failure:
                    return operation_result

                has_acceso_validation = await self.has_access_operation(
                    rol_id=rol_id, acceso_id=access_id, operation_id=operation_id
                )
                if has_acceso_validation.is_success:
                    for access_operation in rol.access_operation:
                        if (
                            access_operation.acceso_id == access_id
                            and access_operation.operation_id == operation_id
                        ):
                            access_operation_to_delete.append(access_operation)

                            break

        rol.access_operation = [
            access_operation
            for access_operation in rol.access_operation
            if access_operation not in access_operation_to_delete
        ]

        await self.rol_acceso_operation_repository.delete_all(
            access_operation_to_delete
        )

        return Success(RolSchema.model_validate(rol))
