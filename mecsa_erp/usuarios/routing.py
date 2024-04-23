from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select, insert
from sqlalchemy.exc import IntegrityError

from config.database import get_session
from mecsa_erp.usuarios.models import *


router = APIRouter(tags=["Usuarios"], prefix="/usuarios")


###################################
############# CLASES ##############
###################################
class UsuarioList(SQLModel):
    data: list[Usuario]

class UsuarioRolesAccesos(SQLModel):
    usuario: Usuario
    roles: list[Rol]
    accesos: list[Acceso]

class UsuarioRegistrar(BaseModel):
    username: str
    password: str
    email: str
    display_name: str
    rol_ids: list[int]
    acceso_ids: list[int]


####################################
######## REGISTRAR USUARIO #########
####################################
@router.post("/register")
def register_usuario(user_request: UsuarioRegistrar, session: Session = Depends(get_session)):
    nuevo_usuario = Usuario(
        username=user_request.username,
        password=user_request.password,  # HASHEAR
        email=user_request.email,
        display_name=user_request.display_name
    )
     
    try:
        session.add(nuevo_usuario)
        session.commit()
        for rol_id in user_request.rol_ids:
            nuevo_usuario_rol = UsuarioRol(usuario_id=nuevo_usuario.username, rol_id=rol_id)
            session.add(nuevo_usuario_rol)

        for acceso_id in user_request.acceso_ids:
            nuevo_usuario_accesos = UsuarioAcceso(usuario_id=nuevo_usuario.username, acceso_id=acceso_id)
            session.add(nuevo_usuario_accesos)

        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el usuario, posiblemente duplicado o datos inválidos")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Usuario registrado con éxito"}


####################################
######### LISTAR USUARIOS ##########
####################################
@router.get("/usuarios", response_model=UsuarioList)
def get_usuarios(session: Session = Depends(get_session)):
    tabla = select(Usuario)
    usuarios = session.exec(tabla).all()
    return UsuarioList(data=usuarios)


####################################
#### ROLES Y ACCESOS DE USUARIO ####
####################################
@router.get("/{username}/roles-accesos", response_model=UsuarioRolesAccesos)
def get_usuario_roles_accesos(username: str, session: Session = Depends(get_session)):
    ##### USUARIO POR USERNAME #####
    usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    ##### ROLES DE USUARIO #####
    usuario_roles = session.exec(
        select(Rol).join(UsuarioRol, UsuarioRol.rol_id == Rol.rol_id)
        .where(UsuarioRol.usuario_id == username)
    ).all()

    ##### ACCESOS DEL USUARIO #####
    usuario_accesos = session.exec(
        select(Acceso).join(UsuarioAcceso, UsuarioAcceso.acceso_id == Acceso.acceso_id)
        .where(UsuarioAcceso.usuario_id == username)
    ).all()

    return UsuarioRolesAccesos(usuario=usuario, roles=usuario_roles, accesos=usuario_accesos)