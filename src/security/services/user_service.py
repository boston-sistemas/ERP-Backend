from datetime import datetime
from re import findall as re_search

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.security.failures import UserFailures
from src.security.models import Usuario, UsuarioRol
from src.security.repositories import UserRepository, UserRolRepository
from src.security.schemas import (
    UsuarioCreateSchema,
    UsuarioCreateWithRolesSchema,
    UsuarioUpdateSchema,
)

from .rol_service import RolService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MIN_LENGTH_PASSWORD = 12
MIN_UPPER_PASSWORD = 2
MIN_LOWER_PASSWORD = 1
MIN_DIGIT_PASSWORD = 1
MIN_SYMBOL_PASSWORD = 1


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = UserRepository(db)
        self.rol_service = RolService(db)
        self.user_rol_repository = UserRolRepository(db)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password, rounds=12)

    @staticmethod
    def is_password_secure(password: str) -> bool:
        if len(password) < MIN_LENGTH_PASSWORD:
            return False

        if len(re_search(r"[a-z]", password)) < MIN_LOWER_PASSWORD:
            return False

        if len(re_search(r"[A-Z]", password)) < MIN_UPPER_PASSWORD:
            return False

        if len(re_search(r"[0-9]", password)) < MIN_DIGIT_PASSWORD:
            return False

        if len(re_search(r"[\W_]", password)) < MIN_SYMBOL_PASSWORD:
            return False
        return True

    async def read_user(
        self, user_id: int, include_roles: bool = False
    ) -> Result[Usuario, CustomException]:
        user = await self.repository.find_user(
            Usuario.usuario_id == user_id, include_roles=include_roles
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
        self, user_data: UsuarioCreateSchema | dict
    ) -> Result[Usuario, CustomException]:
        user_dict = user_data if isinstance(user_data, dict) else user_data.model_dump()

        validation_result = await self.validate_user_data(user_dict["username"])
        if validation_result.is_failure:
            return validation_result

        user = Usuario(**user_dict, reset_password_at=datetime.now())
        user.password = self.get_password_hash(user.password)

        await self.repository.save(user)

        return Success(user)

    def _create_user_with_roles_in_single_commit(func):
        async def wrapper(self, *args, **kwargs):
            self.repository.commit = False
            self.repository.flush = True
            # TODO: reiniciar los valores?
            return await func(self, *args, **kwargs)

        return wrapper

    @_create_user_with_roles_in_single_commit
    async def create_user_with_roles(
        self, user_data: UsuarioCreateWithRolesSchema
    ) -> Result[None, CustomException]:
        creation_result = await self.create_user(
            user_data.model_dump(exclude={"rol_ids"})
        )
        if creation_result.is_failure:
            return creation_result

        user: Usuario = creation_result.value
        add_roles_result = await self._add_roles_to_user_instance(
            user=user, rol_ids=user_data.rol_ids
        )
        if add_roles_result.is_failure:
            return UserFailures.ROLE_NOT_FOUND_WHEN_CREATING_FAILURE

        return Success(None)

    async def update_user(
        self, user_id: int, update_data: UsuarioUpdateSchema
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(user_id, include_roles=False)
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

    async def delete_user(self, user_id: int) -> Result[None, CustomException]:
        user_result = await self.read_user(user_id)
        if user_result.is_failure:
            return user_result

        user: Usuario = user_result.value
        await self.repository.delete(user)

        return Success(None)

    async def has_rol(
        self, user_id: int, rol_id: int
    ) -> Result[UsuarioRol, CustomException]:
        has_rol, user_rol = await self.user_rol_repository.exists(
            (UsuarioRol.usuario_id == user_id) & (UsuarioRol.rol_id == rol_id)
        )

        if has_rol:
            return Success(user_rol)

        return UserFailures.USER_ROLE_NOT_FOUND_FAILURE

    async def _add_roles_to_user_instance(
        self, user: Usuario, rol_ids: list[int]
    ) -> Result[None, CustomException]:
        user_id: str = user.usuario_id

        roles_to_add = []
        for rol_id in set(rol_ids):
            rol_result = await self.rol_service.read_rol(rol_id)
            if rol_result.is_failure:
                return UserFailures.ROLE_NOT_FOUND_WHEN_ADDING_FAILURE

            has_rol_validation = await self.has_rol(user_id, rol_id)
            if has_rol_validation.is_success:
                return UserFailures.USER_HAS_ROLE_WHEN_ADDING_FAILURE

            rol = rol_result.value
            roles_to_add.append(UsuarioRol(usuario_id=user_id, rol_id=rol.rol_id))

        await self.user_rol_repository.save_all(roles_to_add)

        return Success(None)

    async def add_roles_to_user(
        self, user_id: int, rol_ids: list[int]
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(user_id=user_id)
        if user_result.is_failure:
            return user_result

        return await self._add_roles_to_user_instance(
            user=user_result.value, rol_ids=rol_ids
        )

    async def delete_roles_from_user(
        self, user_id: int, rol_ids: list[int]
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(user_id)
        if user_result.is_failure:
            return user_result

        roles_to_delete = []
        for rol_id in set(rol_ids):
            rol_result = await self.rol_service.read_rol(rol_id)
            if rol_result.is_failure:
                return UserFailures.ROLE_NOT_FOUND_WHEN_ADDING_FAILURE

            has_rol_validation = await self.has_rol(user_id, rol_id)
            if has_rol_validation.is_failure:
                return UserFailures.USER_MISSING_ROLE_WHEN_DELETING_FAILURE

            roles_to_delete.append(has_rol_validation.value)

        await self.user_rol_repository.delete_all(roles_to_delete)

        return Success(None)

    async def update_password(
        self, user_id: int, new_password: str
    ) -> Result[None, CustomException]:
        user_result = await self.read_user(user_id)
        if user_result.is_failure:
            return user_result

        user: Usuario = user_result.value

        if not self.is_password_secure(new_password):
            return UserFailures.USER_UPDATE_PASSWORD_FAILURE

        user.password = self.get_password_hash(new_password)
        user.reset_password_at = datetime.now()

        await self.repository.save(user)

        return Success(None)
