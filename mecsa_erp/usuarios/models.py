from sqlalchemy import ForeignKeyConstraint
from sqlmodel import SQLModel, Field

class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    
    username: str = Field(primary_key=True)
    password: str
    email: str
    display_name: str


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    rol_id: int = Field(primary_key=True)
    nombre: str

class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: str = Field(primary_key=True)
    rol_id: int = Field(primary_key=True)
 
    __table_args__ = (
        ForeignKeyConstraint(['usuario_id'], ['usuario.username']),
        ForeignKeyConstraint(['rol_id'], ['rol.rol_id'])
    )

class UsuarioAcceso(SQLModel, table=True):
    __tablename__ = "usuario_acceso"

    usuario_id: str = Field(primary_key=True)
    acceso_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['usuario_id'], ['usuario.username']),
        ForeignKeyConstraint(['acceso_id'], ['acceso.acceso_id'])
    )

class Acceso(SQLModel, table=True):
    __tablename__ = "acceso"

    acceso_id: int = Field(primary_key=True)
    nombre: str
    
class Rol_acceso(SQLModel, table=True):
    __tablename__ = "rol_acceso"

    rol_id: int = Field(primary_key=True)
    acceso_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['rol_id'], ['rol.rol_id']),
        ForeignKeyConstraint(['acceso_id'], ['acceso.acceso_id'])
    )