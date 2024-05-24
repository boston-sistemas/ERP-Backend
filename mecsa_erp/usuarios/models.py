from sqlalchemy import Column, ForeignKeyConstraint, Identity, Integer
from sqlmodel import Relationship, SQLModel, Field


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: int = Field(primary_key=True)
    rol_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["usuario_id"], ["usuario.usuario_id"], ondelete="CASCADE"),
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

    usuario_id: int = Field(default=None, sa_column=Column(Integer, Identity(start=1), primary_key=True))
    username: str = Field(unique=True)
    password: str
    email: str = Field(unique=True)
    display_name: str

    roles: list["Rol"] = Relationship(back_populates="usuarios", link_model=UsuarioRol)


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    rol_id: int = Field(default=None, sa_column=Column(Integer, Identity(start=1), primary_key=True))
    nombre: str = Field(unique=True)
    is_active: bool = Field(default=True)

    usuarios: list[Usuario] = Relationship(
        back_populates="roles", link_model=UsuarioRol
    )
    accesos: list["Acceso"] = Relationship(back_populates="roles", link_model=RolAcceso)


class Acceso(SQLModel, table=True):
    __tablename__ = "acceso"

    acceso_id: int = Field(default=None, sa_column=Column(Integer, Identity(start=1), primary_key=True))
    nombre: str = Field(unique=True)
    is_active: bool = Field(default=True)

    roles: list[Rol] = Relationship(back_populates="accesos", link_model=RolAcceso)
