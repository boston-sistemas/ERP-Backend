from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import (
    TIMESTAMP,
    ForeignKeyConstraint,
    Identity,
    PrimaryKeyConstraint,
    String,
    and_,
    func,
)
from sqlalchemy.dialects.oracle import CLOB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.security.constants import (
    ACTION_MAX_LENGTH,
    ENDPOINT_NAME_MAX_LENGTH,
    ENTITY_TYPE_MAX_LENGTH,
    MAX_LENGTH_ACCESO_DESCRIPTION,
    MAX_LENGTH_ACCESO_IMAGE_PATH,
    MAX_LENGTH_ACCESO_NOMBRE,
    MAX_LENGTH_ACCESO_SCOPE,
    MAX_LENGTH_ACCESO_VIEW_PATH,
    MAX_LENGTH_MODULO_IMAGE_PATH,
    MAX_LENGTH_MODULO_NOMBRE,
    MAX_LENGTH_OPERATION_NAME,
    MAX_LENGTH_ROL_NOMBRE,
    MAX_LENGTH_SESION_IP,
    MAX_LENGTH_TOKEN_AUTENTICACION_CODIGO,
    MAX_LENGTH_USUARIO_DISPLAY_NAME,
    MAX_LENGTH_USUARIO_EMAIL,
    MAX_LENGTH_USUARIO_PASSWORD,
    MAX_LENGTH_USUARIO_USERNAME,
    PARAMETER_CATEGORY_NAME_MAX_LENGTH,
    PARAMETER_DATATYPE_MAX_LENGTH,
    PARAMETER_DESCRIPTION_MAX_LENGTH,
    PARAMETER_VALUE_MAX_LENGTH,
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
    reset_password_at: Mapped[datetime] = mapped_column()
    roles: Mapped[list["Rol"]] = relationship(secondary="usuario_rol", lazy="noload")

    __table_args__ = (PrimaryKeyConstraint("usuario_id"),)

    def __repr__(self):
        return f"<Usuario(id='{self.usuario_id}',username='{self.username}', email='{self.email}')>"


class AccessOperation(Base):
    __tablename__ = "acceso_operacion"

    acceso_id: Mapped[int] = mapped_column()
    operation_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("acceso_id", "operation_id"),
        ForeignKeyConstraint(["acceso_id"], ["acceso.acceso_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["operation_id"], ["operacion.id"], ondelete="CASCADE"),
    )


class RolAccesoOperation(Base):
    __tablename__ = "rol_acceso_operacion"

    rol_id: Mapped[int] = mapped_column()
    acceso_id: Mapped[int] = mapped_column()
    operation_id: Mapped[int] = mapped_column()

    # rol: Mapped["Rol"] = relationship(
    #     "Rol",
    #     lazy="noload",
    #     primaryjoin=lambda: and_(
    #         Rol.rol_id == RolAccesoOperation.rol_id,
    #     ),
    #     foreign_keys=lambda: [RolAccesoOperation.rol_id],
    # )

    acceso: Mapped["Acceso"] = relationship(
        "Acceso",
        lazy="noload",
        primaryjoin=lambda: and_(
            Acceso.acceso_id == RolAccesoOperation.acceso_id,
        ),
        foreign_keys=lambda: [RolAccesoOperation.acceso_id],
    )

    operation: Mapped["Operation"] = relationship(
        "Operation",
        lazy="noload",
        primaryjoin=lambda: and_(
            Operation.id == RolAccesoOperation.operation_id,
        ),
        foreign_keys=lambda: [RolAccesoOperation.operation_id],
    )

    __table_args__ = (
        PrimaryKeyConstraint("rol_id", "acceso_id", "operation_id"),
        ForeignKeyConstraint(["rol_id"], ["rol.rol_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(
            ["acceso_id", "operation_id"],
            ["acceso_operacion.acceso_id", "acceso_operacion.operation_id"],
            ondelete="CASCADE",
        ),
    )


class Rol(Base):
    __tablename__ = "rol"

    rol_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ROL_NOMBRE), unique=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    rol_color: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ROL_NOMBRE), default="bg-zinc-400"
    )

    access_operation: Mapped[list["RolAccesoOperation"]] = relationship(
        "RolAccesoOperation",
        lazy="noload",
        primaryjoin=lambda: and_(
            Rol.rol_id == RolAccesoOperation.rol_id,
        ),
        foreign_keys=lambda: [RolAccesoOperation.rol_id],
    )

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


class Operation(Base):
    __tablename__ = "operacion"

    id: Mapped[int] = mapped_column(Identity(start=1))
    name: Mapped[str] = mapped_column(String(length=MAX_LENGTH_OPERATION_NAME))

    __table_args__ = (PrimaryKeyConstraint("id"),)


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


class ModuloSistema(Base):
    __tablename__ = "modulo_sistema"

    id: Mapped[int] = mapped_column(Identity(start=1))
    name: Mapped[str] = mapped_column(String(length=MAX_LENGTH_MODULO_NOMBRE))
    is_active: Mapped[bool] = mapped_column(default=True)
    image_path: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_MODULO_IMAGE_PATH)
    )

    __table_args__ = (PrimaryKeyConstraint("id"),)


class Acceso(Base):
    __tablename__ = "acceso"

    acceso_id: Mapped[int] = mapped_column(Identity(start=1))
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ACCESO_NOMBRE), unique=True
    )
    modulo_id: Mapped[int] = mapped_column()
    view_path: Mapped[str] = mapped_column(String(length=MAX_LENGTH_ACCESO_VIEW_PATH))
    image_path: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_ACCESO_IMAGE_PATH)
    )
    description: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_ACCESO_DESCRIPTION)
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    operations: Mapped[list["Operation"]] = relationship(
        "Operation",
        secondary="acceso_operacion",
        lazy="noload",
        viewonly=True,
    )

    access_operations: Mapped[list["AccessOperation"]] = relationship(
        "AccessOperation",
        lazy="noload",
        primaryjoin=lambda: and_(
            Acceso.acceso_id == AccessOperation.acceso_id,
        ),
        foreign_keys=lambda: [AccessOperation.acceso_id],
        viewonly=True,
    )

    rol_accesses_operations: Mapped[list["RolAccesoOperation"]] = relationship(
        "RolAccesoOperation",
        lazy="noload",
        primaryjoin=lambda: and_(
            Acceso.acceso_id == RolAccesoOperation.acceso_id,
        ),
        foreign_keys=lambda: [RolAccesoOperation.acceso_id],
        viewonly=True,
    )

    __table_args__ = (
        PrimaryKeyConstraint("acceso_id"),
        ForeignKeyConstraint(["modulo_id"], ["modulo_sistema.id"]),
    )


class UsuarioSesion(Base):
    __tablename__ = "usuario_sesion"

    sesion_id: Mapped[UUID] = mapped_column()
    usuario_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    not_after: Mapped[datetime] = mapped_column()
    ip: Mapped[str] = mapped_column(String(length=MAX_LENGTH_SESION_IP))

    usuario: Mapped["Usuario"] = relationship(lazy="noload")

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


class ParameterCategory(Base):
    __tablename__ = "parameter_categories"

    id: Mapped[int] = mapped_column(Identity(start=120), primary_key=True)
    name: Mapped[str] = mapped_column(
        String(length=PARAMETER_CATEGORY_NAME_MAX_LENGTH), unique=True
    )


class Parameter(Base):
    __tablename__ = "parameters"

    id: Mapped[int] = mapped_column(Identity(start=1050), primary_key=True)
    category_id: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(
        String(length=PARAMETER_DESCRIPTION_MAX_LENGTH), nullable=True
    )
    data_type: Mapped[str] = mapped_column(String(length=PARAMETER_DATATYPE_MAX_LENGTH))
    value: Mapped[str] = mapped_column(String(length=PARAMETER_VALUE_MAX_LENGTH))
    is_active: Mapped[bool] = mapped_column(default=True)

    category: Mapped[ParameterCategory] = relationship(lazy="noload")

    __table_args__ = (
        ForeignKeyConstraint(["category_id"], ["parameter_categories.id"]),
    )


class AuditActionLog(Base):
    __tablename__ = "audit_action_log"

    id: Mapped[UUID] = mapped_column()
    user_id: Mapped[int] = mapped_column(nullable=True)
    endpoint_name: Mapped[str] = mapped_column(String(ENDPOINT_NAME_MAX_LENGTH))
    action: Mapped[str] = mapped_column(String(ACTION_MAX_LENGTH))
    query_params: Mapped[str] = mapped_column(CLOB, nullable=True)
    request_data: Mapped[str] = mapped_column(CLOB, nullable=True)
    response_data: Mapped[str] = mapped_column(CLOB, nullable=True)
    status_code: Mapped[int] = mapped_column()
    ip: Mapped[str] = mapped_column(String(MAX_LENGTH_SESION_IP))
    at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    audit_data_logs: Mapped[list["AuditDataLog"]] = relationship(
        "AuditDataLog",
        lazy="noload",
        primaryjoin=lambda: and_(
            AuditActionLog.id == AuditDataLog.action_id,
        ),
        foreign_keys=lambda: [AuditDataLog.action_id],
    )

    __table_args__ = (PrimaryKeyConstraint("id"),)


class AuditDataLog(Base):
    __tablename__ = "audit_data_log"

    id: Mapped[int] = mapped_column(Identity(start=1))
    entity_type: Mapped[str] = mapped_column(String(ENTITY_TYPE_MAX_LENGTH))
    action: Mapped[str] = mapped_column(String(ACTION_MAX_LENGTH))
    old_data: Mapped[str] = mapped_column(CLOB, nullable=True)
    new_data: Mapped[str] = mapped_column(CLOB, nullable=True)
    at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    action_id: Mapped[UUID] = mapped_column()

    __table_args__ = (PrimaryKeyConstraint("id"),)
