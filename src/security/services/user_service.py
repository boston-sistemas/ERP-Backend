from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import UserFailures
from src.security.models import Usuario, UsuarioRol
from src.security.repositories import RolRepository, UserRepository, UserRolRepository
from src.security.schemas import (
    UsuarioCreateSchema,
    UsuarioUpdateSchema,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = UserRepository(db)
        self.rol_repository = RolRepository(db)
        self.user_rol_repository = UserRolRepository(db)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password, rounds=12)

    async def read_user(
        self, id: int, include_roles: bool = False
    ) -> Result[Usuario, CustomException]:
        user = await self.repository.find_user(
            Usuario.usuario_id == id, include_roles=include_roles
        )
        if user is not None:
            return Success(user)

        return UserFailures.USER_NOT_FOUND_FAILURE

    async def read_user_by_username(
        self, username: str, include_roles: bool = False
    ) -> Result[Usuario, CustomException]:
        user = await self.repository.find_user(
            Usuario.username == username, include_roles=include_roles
        )

        if user is not None:
            return Success(user)

        return UserFailures.USER_NOT_FOUND_FAILURE

    async def read_users(self) -> list[Usuario]:
        return await self.repository.find_all(
            options=(self.repository.include_roles(),), apply_unique=True
        )

    async def validate_user_data(
        self, username: str | None = None
    ) -> Result[None, CustomException]:
        username_exists = username and (
            await self.repository.find(Usuario.username == username)
        )

        if username_exists:
            return UserFailures.USERNAME_ALREADY_EXISTS_FAILURE(username)

        return Success(None)

    async def create_user(
        self, user_data: UsuarioCreateSchema
    ) -> Result[None, CustomException]:
        validation_result = await self.validate_user_data(user_data.username)
        if validation_result.is_failure:
            return validation_result

        user = Usuario(**user_data.model_dump(exclude={"rol_ids"}))
        user.password = self.get_password_hash(user.password)

        if user_data.rol_ids:
            for rol_id in set(user_data.rol_ids):
                rol = await self.rol_repository.find_by_id(rol_id)  # TODO: RolService?
                if rol is None:
                    return UserFailures.ROLE_NOT_FOUND_WHEN_CREATING_FAILURE

                user.roles.append(rol)

        await self.repository.save(user)

        return Success(None)

    async def update_user(
        self, id: int, update_data: UsuarioUpdateSchema
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(id, include_roles=False)
        if user_result.is_failure:
            return user_result

        validation_result = await self.validate_user_data(update_data.username)
        if validation_result.is_failure:
            return validation_result

        user: Usuario = user_result.value

        for key, value in update_data.model_dump(exclude_none=True).items():
            setattr(user, key, value)

        await self.repository.save(user)

        return Success(None)

    async def delete_user(self, id: int) -> Result[None, CustomException]:
        user_result = await self.read_user(id)
        if user_result.is_failure:
            return user_result

        user: Usuario = user_result.value
        await self.repository.delete(user)

        return Success(None)

    @staticmethod
    def has_rol_instance(user: Usuario, rol_id: int) -> bool:
        return any(rol.rol_id == rol_id for rol in user.roles)

    async def has_rol(
        self, user_id: int, rol_id: int
    ) -> Result[UsuarioRol, CustomException]:
        has_rol, user_rol = await self.user_rol_repository.exists(
            (UsuarioRol.usuario_id == user_id) & (UsuarioRol.rol_id == rol_id)
        )

        if has_rol:
            return Success(user_rol)

        return UserFailures.USER_ROLE_NOT_FOUND_FAILURE

    async def add_roles_to_user(
        self, id: int, rol_ids: list[int]
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(id)
        if user_result.is_failure:
            return user_result

        roles_to_add = []
        for rol_id in set(rol_ids):
            rol = await self.rol_repository.find_by_id(rol_id)  # TODO: RolService?
            if rol is None:
                return UserFailures.ROLE_NOT_FOUND_WHEN_ADDING_FAILURE

            has_rol_validation = await self.has_rol(id, rol_id)
            if has_rol_validation.is_success:
                return UserFailures.USER_HAS_ROLE_WHEN_ADDING_FAILURE

            roles_to_add.append(UsuarioRol(usuario_id=id, rol_id=rol.rol_id))

        await self.user_rol_repository.save_all(roles_to_add)

        return Success(None)

    async def delete_roles_from_user(
        self, id: int, rol_ids: list[int]
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(id)
        if user_result.is_failure:
            return user_result

        roles_to_delete = []
        for rol_id in set(rol_ids):
            rol = await self.rol_repository.find_by_id(rol_id)  # TODO: RolService?
            if rol is None:
                return UserFailures.ROLE_NOT_FOUND_WHEN_DELETING_FAILURE

            has_rol_validation = await self.has_rol(id, rol_id)
            if has_rol_validation.is_failure:
                return UserFailures.USER_MISSING_ROLE_WHEN_DELETING_FAILURE

            roles_to_delete.append(has_rol_validation.value)

        await self.user_rol_repository.delete_all(roles_to_delete)

        return Success(None)
