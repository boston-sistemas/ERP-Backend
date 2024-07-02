from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.elements import BinaryExpression

from src.core.database import Base
from src.security.models import Acceso, Rol, RolAcceso
from src.security.schemas.full import RolCreateSchema, RolUpdateSchema

ModelType = TypeVar("ModelType", bound=Base)


class RolService:
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    async def read_model_by_parameter(
        self, model: Generic[ModelType], filter: BinaryExpression
    ) -> Rol:
        stmt = select(model).where(filter)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def read_rols(self) -> list[Rol]:
        stmt = select(Rol)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_rol(self, data: RolCreateSchema) -> Rol:
        rol = Rol(nombre=data.nombre, is_active=data.is_active)
        self.db.add(rol)
        self.db.flush()

        if data.acceso_ids:
            for acceso_id in set(data.acceso_ids):
                acceso = await self.read_model_by_parameter(
                    Acceso, Acceso.acceso_id == acceso_id
                )
                if acceso:
                    rol_acceso = RolAcceso(rol_id=rol.rol_id, acceso_id=acceso_id)
                    self.db.add(rol_acceso)

        if self.commit:
            await self.db.commit()
            await self.db.refresh(rol)

        return rol

    async def update_rol(self, rol: Rol, data: RolUpdateSchema) -> Rol:
        update_rol = data.dict(exclude_unset=True)
        for key, value in update_rol.items():
            setattr(rol, key, value)

        if self.commit:
            await self.db.commit()
            await self.db.refresh(rol)
        return rol

    async def delete_rol(self, rol: Rol) -> str:
        await self.db.delete(rol)
        if self.commit:
            await self.db.commit()
        return "Rol eliminado correctamente"

    async def create_access_to_rol(self, rol_id: int, acceso_ids: list[int]) -> None:
        for acceso_id in set(acceso_ids):
            acceso = await self.read_model_by_parameter(
                Acceso, Acceso.acceso_id == acceso_id
            )
            if acceso:
                exist = await self.read_model_by_parameter(
                    RolAcceso,
                    (RolAcceso.rol_id == rol_id) & (RolAcceso.acceso_id == acceso_id),
                )
                if not exist:
                    rol_acceso = RolAcceso(rol_id=rol_id, acceso_id=acceso_id)
                    self.db.add(rol_acceso)

        if self.commit:
            await self.db.commit()

    async def delete_access_to_rol(self, rol_id: int, acceso_ids: list[int]) -> str:
        for acceso_id in set(acceso_ids):
            exist = await self.read_model_by_parameter(
                RolAcceso,
                (RolAcceso.rol_id == rol_id) & (RolAcceso.acceso_id == acceso_id),
            )
            if exist:
                await self.db.delete(exist)
            else:
                return str(acceso_id)

        if self.commit:
            await self.db.commit()

        return None

    async def refresh_rol(self, rol: Rol) -> Rol:
        await self.db.refresh(rol)
        return rol
