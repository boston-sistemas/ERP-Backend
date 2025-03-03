from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import AccesoFailures
from src.security.models import Acceso, AccessOperation, Operation
from src.security.repositories import AccesoRepository
from src.security.schemas import (
    AccesoListSchema,
    AccesoSchema,
    AccessCreateSchema,
    AccessUpdateSchema,
    SystemModuleSchema,
)

from .operation_service import OperationService
from .system_module_service import SystemModuleService


class AccesoService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = AccesoRepository(db)
        self.system_module_service = SystemModuleService(db=db)
        self.operation_service = OperationService(db=db)

    async def _read_access(
        self,
        access_id: int,
        include_operations: bool = False,
        include_access_operations: bool = False,
        include_rol_accesses_operations: bool = False,
    ) -> Result[Acceso, CustomException]:
        access: Acceso = await self.repository.find_access(
            access_id=access_id,
            include_operations=include_operations,
            include_access_operations=include_access_operations,
            include_rol_accesses_operations=include_rol_accesses_operations,
        )

        if access is None:
            return AccesoFailures.ACCESO_NOT_FOUND_FAILURE

        return Success(access)

    async def read_acceso(
        self,
        acceso_id: int,
        include_operations: bool = False,
    ) -> Result[AccesoSchema, CustomException]:
        access: Success = await self._read_access(
            access_id=acceso_id,
            include_operations=include_operations,
        )

        if access.is_failure:
            return access

        return Success(AccesoSchema.model_validate(access.value))

    async def read_accesos(self) -> list[Acceso]:
        access: list[Acceso] = await self.repository.find_accessess()

        return Success(
            AccesoListSchema(
                accesos=access,
            )
        )

    async def _validate_access_update_data(
        self,
        data: AccessUpdateSchema,
        access: Acceso,
    ) -> Result[None, CustomException]:
        if data.name != access.nombre:
            validation_result: list[Acceso] = await self.repository.find_accessess(
                name=data.name
            )

            if validation_result:
                return AccesoFailures.ACCESS_NAME_ALREADY_EXISTS_FAILURE

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

    async def _validate_access_data(
        self,
        data: AccessCreateSchema,
    ) -> Result[None, CustomException]:
        validation_result: list[Acceso] = await self.repository.find_accessess(
            name=data.name
        )

        if validation_result:
            return AccesoFailures.ACCESS_NAME_ALREADY_EXISTS_FAILURE

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

        access = await self.repository.save(access, flush=True)

        accessess_operations = []

        for operation_id in form.operations:
            print(operation_id)
            validation_result: Success = await self.operation_service._read_operation(
                operation_id=operation_id
            )

            if validation_result.is_failure:
                return validation_result

            operation: Operation = validation_result.value

            access_operation: AccessOperation = AccessOperation(
                operation_id=operation_id,
                acceso_id=access.acceso_id,
            )

            if any(
                ac_op.acceso_id == access.acceso_id
                and ac_op.operation_id == operation_id
                for ac_op in accessess_operations
            ):
                continue

            accessess_operations.append(access_operation)

            access.operations.append(operation)

            await self.repository.expunge(operation)

        await self.repository.save_all(accessess_operations)

        return Success(AccesoSchema.model_validate(access))

    async def update_access(
        self,
        access_id: int,
        form: AccessCreateSchema,
    ) -> Result[AccesoSchema, CustomException]:
        access: Success = await self._read_access(
            access_id=access_id,
            include_access_operations=True,
            include_rol_accesses_operations=True,
        )

        if access.is_failure:
            return access

        access: Acceso = access.value

        validation_result: Success = await self._validate_access_update_data(
            data=form, access=access
        )

        if validation_result.is_failure:
            return validation_result

        access.nombre = form.name
        access.modulo_id = form.system_module_id
        access.view_path = form.view_path
        access.image_path = form.image_path
        access.description = form.description
        access.is_active = form.is_active

        access = await self.repository.save(access, flush=True)

        access_operations_to_delete = [
            ac_op
            for ac_op in access.access_operations
            if ac_op.operation_id not in set(form.operations)
        ]

        if access_operations_to_delete:
            await self.repository.delete_all(access_operations_to_delete, flush=True)

        rol_access_operations_to_delete = [
            rol_access
            for rol_access in access.rol_accesses_operations
            if rol_access.acceso_id == access.acceso_id
            and rol_access.operation_id not in set(form.operations)
        ]

        if rol_access_operations_to_delete:
            await self.repository.delete_all(
                rol_access_operations_to_delete, flush=True
            )

        accessess_operations = []

        for operation_id in form.operations:
            validation_result: Success = await self.operation_service._read_operation(
                operation_id=operation_id
            )

            if validation_result.is_failure:
                return validation_result

            operation: Operation = validation_result.value

            access_operation: AccessOperation = AccessOperation(
                operation_id=operation_id,
                acceso_id=access.acceso_id,
            )

            if any(
                ac_op.acceso_id == access.acceso_id
                and ac_op.operation_id == operation_id
                for ac_op in accessess_operations
            ):
                continue

            access.operations.append(operation)

            await self.repository.expunge(operation)
            if any(
                ac_op.operation_id == operation_id for ac_op in access.access_operations
            ):
                continue
            accessess_operations.append(access_operation)

        await self.repository.save_all(accessess_operations)

        return Success(AccesoSchema.model_validate(access))
