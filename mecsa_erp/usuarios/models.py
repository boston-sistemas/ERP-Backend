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
        ForeignKeyConstraint(['usuario_id'], ['usuario.username'], ondelete='CASCADE'),
        ForeignKeyConstraint(['rol_id'], ['rol.rol_id'], ondelete='CASCADE'),
    )

class UsuarioAcceso(SQLModel, table=True):
    __tablename__ = "usuario_acceso"

    usuario_id: str = Field(primary_key=True)
    acceso_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['usuario_id'], ['usuario.username'], ondelete='CASCADE'),
        ForeignKeyConstraint(['acceso_id'], ['acceso.acceso_id'], ondelete='CASCADE'),
    )

class Acceso(SQLModel, table=True):
    __tablename__ = "acceso"

    acceso_id: int = Field(primary_key=True)
    nombre: str
    
class RolAcceso(SQLModel, table=True):
    __tablename__ = "rol_acceso"

    rol_id: int = Field(primary_key=True)
    acceso_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['rol_id'], ['rol.rol_id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['acceso_id'], ['acceso.acceso_id'], ondelete='CASCADE'),
    )