from typing import Generic, TypeVar

from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression

from src.core.database import Base
from src.security.models import Acceso, Rol, RolAcceso
from src.security.schemas.full import RolCreateSchema, RolUpdateSchema

ModelType = TypeVar("ModelType", bound=Base)


class RolService:
    def __init__(self, db: Session, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    def read_model_by_parameter(
        self, model: Generic[ModelType], filter: BinaryExpression
    ) -> Rol:
        stmt = select(model).where(filter)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def read_rols(self) -> list[Rol]:
        stmt = select(Rol)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def create_rol(self, data: RolCreateSchema) -> Rol:
        rol = Rol(nombre=data.nombre, is_active=data.is_active)
        self.db.add(rol)
        self.db.flush()

        if data.acceso_ids:
            for acceso_id in set(data.acceso_ids):
                acceso = self.read_model_by_parameter(
                    Acceso, Acceso.acceso_id == acceso_id
                )
                if acceso:
                    rol_acceso = RolAcceso(rol_id=rol.rol_id, acceso_id=acceso_id)
                    self.db.add(rol_acceso)

        if self.commit:
            self.db.commit()
            self.db.refresh(rol)

        return rol

    def update_rol(self, rol: Rol, data: RolUpdateSchema) -> Rol:
        update_rol = data.dict(exclude_unset=True)
        for key, value in update_rol.items():
            setattr(rol, key, value)

        if self.commit:
            self.db.commit()
            self.db.refresh(rol)
        return rol

    def delete_rol(self, rol: Rol) -> str:
        self.db.delete(rol)
        if self.commit:
            self.db.commit()
        return "Rol eliminado correctamente"

    def create_access_to_rol(self, rol_id: int, acceso_ids: list[int]) -> None:
        for acceso_id in set(acceso_ids):
            acceso = self.read_model_by_parameter(Acceso, Acceso.acceso_id == acceso_id)
            if acceso:
                exist = self.read_model_by_parameter(
                    RolAcceso,
                    (RolAcceso.rol_id == rol_id) & (RolAcceso.acceso_id == acceso_id),
                )
                if not exist:
                    rol_acceso = RolAcceso(rol_id=rol_id, acceso_id=acceso_id)
                    self.db.add(rol_acceso)

        if self.commit:
            self.db.commit()

    def delete_access_to_rol(self, rol_id: int, acceso_ids: list[int]) -> str:
        for acceso_id in set(acceso_ids):
            exist = self.read_model_by_parameter(
                RolAcceso,
                (RolAcceso.rol_id == rol_id) & (RolAcceso.acceso_id == acceso_id),
            )
            if exist:
                self.db.delete(exist)
            else:
                return str(acceso_id)

        if self.commit:
            self.db.commit()

        return None
