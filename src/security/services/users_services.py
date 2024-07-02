from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.elements import BinaryExpression

from src.core.database import Base
from src.security.models import Rol, Usuario, UsuarioRol
from src.security.schemas.full import (
    UsuarioCreateSchema,
    UsuarioUpdateSchema,
)

ModelType = TypeVar("ModelType", bound=Base)


class UserService:
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    async def read_model_by_parameter(
        self, model: Generic[ModelType], filter: BinaryExpression
    ) -> Generic[ModelType]:
        stmt = select(model).where(filter)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def read_users(self) -> list[Usuario]:
        stmt = select(Usuario)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_user(self, data: UsuarioCreateSchema) -> Usuario:
        user = Usuario(
            username=data.username,
            display_name=data.display_name,
            email=data.email,
            password=data.password,
        )

        self.db.add(user)
        # Revisar despues
        if self.commit:
            await self.db.commit()
            await self.db.refresh(user)

        if data.rol_ids:
            await self.db.flush()
            for rol_id in set(data.rol_ids):
                rol = await self.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
                if rol:
                    user.roles.append(rol)

        if self.commit:
            await self.db.commit()
            await self.db.refresh(user)

        return user

    async def update_user(self, user: Usuario, data: UsuarioUpdateSchema) -> Usuario:
        update_data = data.dict()
        for key, value in update_data.items():
            setattr(user, key, value)

        if self.commit:
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def delete_user(self, user: Usuario) -> str:
        await self.db.delete(user)
        if self.commit:
            await self.db.commit()
        return "Usuario eliminado correctamente"

    async def create_rol_to_user(self, user_id: int, rol_ids: list[int]) -> None:
        for rol_id in set(rol_ids):
            rol = await self.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
            if rol:
                exist = await self.read_model_by_parameter(
                    UsuarioRol,
                    (UsuarioRol.usuario_id == user_id) & (UsuarioRol.rol_id == rol_id),
                )

                if not exist:
                    user_rol = UsuarioRol(usuario_id=user_id, rol_id=rol_id)
                    self.db.add(user_rol)

        if self.commit:
            await self.db.commit()

    async def delete_rol_to_user(self, user_id: int, rol_ids: list[int]) -> str:
        for rol_id in set(rol_ids):
            exist = await self.read_model_by_parameter(
                UsuarioRol,
                (UsuarioRol.usuario_id == user_id) & (UsuarioRol.rol_id == rol_id),
            )
            if exist:
                await self.db.delete(exist)
            else:
                return str(rol_id)

        if self.commit:
            await self.db.commit()
        return None

    async def refresh_user(self, user: Usuario) -> Usuario:
        await self.db.refresh(user)
        return user
