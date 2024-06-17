from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKeyConstraint, Identity, Integer, String
from sqlmodel import Field, Relationship, SQLModel

from .constants import (
    MAX_LENGTH_ACCESO_NOMBRE,
    MAX_LENGTH_ROL_NOMBRE,
    MAX_LENGTH_SESION_IP,
    MAX_LENGTH_USUARIO_DISPLAY_NAME,
    MAX_LENGTH_USUARIO_EMAIL,
    MAX_LENGTH_USUARIO_PASSWORD,
    MAX_LENGTH_USUARIO_USERNAME,
)


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: int = Field(primary_key=True)
    rol_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(["rol_id"], ["rol.rol_id"], ondelete="CASCADE"),
    )


class RolAcceso(SQLModel, table=True):
    __tablename__ = "rol_acceso"

    rol_id: int = Field(primary_key=True)
    acceso_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["rol_id"], ["rol.rol_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["acceso_id"], ["acceso.acceso_id"], ondelete="CASCADE"),
    )


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    usuario_id: int = Field(
        default=None, sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    username: str = Field(
        unique=True, sa_type=String(length=MAX_LENGTH_USUARIO_USERNAME)
    )
    password: str = Field(sa_type=String(length=MAX_LENGTH_USUARIO_PASSWORD))
    email: str = Field(sa_type=String(length=MAX_LENGTH_USUARIO_EMAIL))
    display_name: str | None = Field(
        sa_type=String(length=MAX_LENGTH_USUARIO_DISPLAY_NAME)
    )
    is_active: bool = Field(default=True)
    blocked_until: datetime | None = Field(default=None)

    roles: list["Rol"] = Relationship(back_populates="usuarios", link_model=UsuarioRol)


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    rol_id: int = Field(
        default=None, sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    nombre: str = Field(unique=True, sa_type=String(length=MAX_LENGTH_ROL_NOMBRE))
    is_active: bool = Field(default=True)

    usuarios: list[Usuario] = Relationship(
        back_populates="roles", link_model=UsuarioRol
    )
    accesos: list["Acceso"] = Relationship(back_populates="roles", link_model=RolAcceso)


class Acceso(SQLModel, table=True):
    __tablename__ = "acceso"

    acceso_id: int = Field(
        default=None, sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    nombre: str = Field(unique=True, sa_type=String(length=MAX_LENGTH_ACCESO_NOMBRE))
    is_active: bool = Field(default=True)

    roles: list[Rol] = Relationship(back_populates="accesos", link_model=RolAcceso)


class Sesion(SQLModel, table=True):
    __tablename__ = "sesion"

    sesion_id: UUID = Field(default_factory=uuid4, primary_key=True)
    usuario_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    # updated_at: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))
    not_after: datetime
    # refreshed_at: datetime | None = None
    # user_agent: str
    ip: str = Field(sa_type=String(length=MAX_LENGTH_SESION_IP))

    usuario: Usuario = Relationship()

    __table_args__ = (
        ForeignKeyConstraint(
            ["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"
        ),
    )
