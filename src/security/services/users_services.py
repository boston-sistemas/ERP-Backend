from typing import Generic, TypeVar

from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression

from src.core.database import Base
from src.security.models import Rol, Usuario, UsuarioRol
from src.security.schemas.full import (
    UsuarioCreateSchema,
    UsuarioUpdateSchema,
)

ModelType = TypeVar("ModelType", bound=Base)


class UserService:
    def __init__(self, db: Session, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    def read_model_by_parameter(
        self, model: Generic[ModelType], filter: BinaryExpression
    ) -> Generic[ModelType]:
        stmt = select(model).where(filter)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def read_users(self) -> list[Usuario]:
        stmt = select(Usuario)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def create_user(self, data: UsuarioCreateSchema) -> Usuario:
        user = Usuario(
            username=data.username,
            display_name=data.display_name,
            email=data.email,
            password=data.password,
        )

        self.db.add(user)
        self.db.flush()

        if data.rol_ids:
            for rol_id in set(data.rol_ids):
                rol = self.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
                if rol:
                    user.roles.append(rol)

        if self.commit:
            self.db.commit()
            self.db.refresh(user)

        return user

    def update_user(self, user: Usuario, data: UsuarioUpdateSchema) -> Usuario:
        update_data = data.dict()
        for key, value in update_data.items():
            setattr(user, key, value)

        if self.commit:
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user: Usuario) -> str:
        self.db.delete(user)
        if self.commit:
            self.db.commit()
        return "Usuario eliminado correctamente"

    def create_rol_to_user(self, user_id: int, rol_ids: list[int]) -> None:
        for rol_id in set(rol_ids):
            rol = self.read_model_by_parameter(Rol, Rol.rol_id == rol_id)
            if rol:
                exist = self.read_model_by_parameter(
                    UsuarioRol,
                    (UsuarioRol.usuario_id == user_id) & (UsuarioRol.rol_id == rol_id),
                )

                if not exist:
                    user_rol = UsuarioRol(usuario_id=user_id, rol_id=rol_id)
                    self.db.add(user_rol)

        if self.commit:
            self.db.commit()

    def delete_rol_to_user(self, user_id: int, rol_ids: list[int]) -> str:
        for rol_id in set(rol_ids):
            exist = self.read_model_by_parameter(
                UsuarioRol,
                (UsuarioRol.usuario_id == user_id) & (UsuarioRol.rol_id == rol_id),
            )
            if exist:
                self.db.delete(exist)
            else:
                return str(rol_id)

        if self.commit:
            self.db.commit()
        return None
