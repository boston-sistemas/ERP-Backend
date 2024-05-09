from fastapi import APIRouter
from sqlmodel import select
from config.database import SessionDependency
from mecsa_erp.usuarios.schemas.usuario import (
    UsuarioCreateSchema,
    UsuarioListSchema,
    RolListSchema,
    AccesoListSchema,
)

from ..models import Acceso, Rol, Usuario

router = APIRouter(tags=["Usuarios"], prefix="/usuarios")


@router.get("/", response_model=UsuarioListSchema)
def get_usuarios(session: SessionDependency):
    statement = select(Usuario)
    usuarios = session.exec(statement).all()
    return UsuarioListSchema(data=usuarios)


@router.post("/")
def create_usuario(session: SessionDependency, usuario: UsuarioCreateSchema):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    usuario.password = pwd_context.hash(usuario.password)
    
    session.add(Usuario(**usuario.model_dump()))
    session.commit()


@router.get("/roles", response_model=RolListSchema)
def get_roles(session: SessionDependency):
    statement = select(Rol)
    roles = session.exec(statement).all()
    return RolListSchema(data=roles)


@router.get("/accesos", response_model=AccesoListSchema)
def get_accesos(session: SessionDependency):
    statement = select(Acceso)
    accesos = session.exec(statement).all()
    return AccesoListSchema(data=accesos)
