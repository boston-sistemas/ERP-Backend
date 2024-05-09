from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Relationship, SQLModel, Field


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: str = Field(primary_key=True)
    rol_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["usuario_id"], ["usuario.username"], ondelete="CASCADE"),
        ForeignKeyConstraint(["rol_id"], ["rol.rol_id"], ondelete="CASCADE"),
    )


class UsuarioAcceso(SQLModel, table=True):
    __tablename__ = "usuario_acceso"

    usuario_id: str = Field(primary_key=True)
    acceso_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["usuario_id"], ["usuario.username"], ondelete="CASCADE"),
        ForeignKeyConstraint(["acceso_id"], ["acceso.acceso_id"], ondelete="CASCADE"),
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

    username: str = Field(primary_key=True)
    password: str
    email: str
    display_name: str

    roles: list["Rol"] = Relationship(back_populates="usuarios", link_model=UsuarioRol)
    accesos: list["Acceso"] = Relationship(
        back_populates="usuarios", link_model=UsuarioAcceso
    )


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    rol_id: int = Field(primary_key=True)
    nombre: str

    usuarios: list[Usuario] = Relationship(
        back_populates="roles", link_model=UsuarioRol
    )
    accesos: list["Acceso"] = Relationship(back_populates="rol", link_model=RolAcceso)


class Acceso(SQLModel, table=True):
    __tablename__ = "acceso"

    acceso_id: int = Field(primary_key=True)
    nombre: str

    usuarios: list[Usuario] = Relationship(
        back_populates="accesos", link_model=UsuarioAcceso
    )
    rol: Rol = Relationship(back_populates="accesos", link_model=RolAcceso)
