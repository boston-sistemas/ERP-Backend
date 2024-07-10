from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    TIMESTAMP,
    ForeignKeyConstraint,
    Identity,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.security.constants import (
    MAX_LENGTH_ACCESO_NOMBRE,
    MAX_LENGTH_ROL_NOMBRE,
    MAX_LENGTH_SESION_IP,
    MAX_LENGTH_USUARIO_DISPLAY_NAME,
    MAX_LENGTH_USUARIO_EMAIL,
    MAX_LENGTH_USUARIO_PASSWORD,
    MAX_LENGTH_USUARIO_USERNAME,
    MAX_LENGTH_TOKEN_AUTENTICACION_CODIGO,
)


class Usuario(Base):
    __tablename__ = "usuario"

    usuario_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    username: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_USUARIO_USERNAME), unique=True
    )
    password: Mapped[str] = mapped_column(String(length=MAX_LENGTH_USUARIO_PASSWORD))
    email: Mapped[str] = mapped_column(String(length=MAX_LENGTH_USUARIO_EMAIL))
    display_name: Mapped[Optional[str]] = mapped_column(
        String(length=MAX_LENGTH_USUARIO_DISPLAY_NAME), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    blocked_until: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    roles: Mapped[list["Rol"]] = relationship(secondary="usuario_rol")

    __table_args__ = (PrimaryKeyConstraint("usuario_id"),)


class Rol(Base):
    __tablename__ = "rol"

    rol_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ROL_NOMBRE), unique=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    accesos: Mapped[list["Acceso"]] = relationship(secondary="rol_acceso")

    __table_args__ = (PrimaryKeyConstraint("rol_id"),)


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    usuario_id: Mapped[int] = mapped_column()
    rol_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("usuario_id", "rol_id"),
        ForeignKeyConstraint(
            ["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(["rol_id"], ["rol.rol_id"], ondelete="CASCADE"),
    )


class RolAcceso(Base):
    __tablename__ = "rol_acceso"

    rol_id: Mapped[int] = mapped_column()
    acceso_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("rol_id", "acceso_id"),
        ForeignKeyConstraint(["rol_id"], ["rol.rol_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["acceso_id"], ["acceso.acceso_id"], ondelete="CASCADE"),
    )


class UsuarioPassword(Base):
    __tablename__ = "usuario_password"

    id: Mapped[int] = mapped_column(Identity(start=1))
    usuario_id: Mapped[int] = mapped_column()
    password: Mapped[str] = mapped_column(String(length=MAX_LENGTH_USUARIO_PASSWORD))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"
        ),
    )


class Acceso(Base):
    __tablename__ = "acceso"

    acceso_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ACCESO_NOMBRE), unique=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (PrimaryKeyConstraint("acceso_id"),)


class UsuarioSesion(Base):
    __tablename__ = "usuario_sesion"

    sesion_id: Mapped[UUID] = mapped_column()
    usuario_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    not_after: Mapped[datetime] = mapped_column()
    ip: Mapped[str] = mapped_column(String(length=MAX_LENGTH_SESION_IP))

    usuario: Mapped["Usuario"] = relationship()

    __table_args__ = (
        PrimaryKeyConstraint("sesion_id"),
        ForeignKeyConstraint(
            ["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"
        ),
    )


class AuthToken(Base):
    __tablename__ = "token_autenticacion"

    id: Mapped[int] = mapped_column(Identity(start=1))
    codigo: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_TOKEN_AUTENTICACION_CODIGO)
    )
    usuario_id: Mapped[int] = mapped_column()
    expiration_at: Mapped[datetime] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"
        ),
    )
