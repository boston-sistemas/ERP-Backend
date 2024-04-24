from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import IntegrityError
from config.database import SessionDependency, get_session
from mecsa_erp.usuarios.models import *
from passlib.context import CryptContext 
from dotenv import load_dotenv
import os
import jwt as pyjwt
from datetime import datetime, timedelta, timezone



###################################
########### FUNCTIONS #############

def create_access_token(data: dict, expires_delta: timedelta = None):
    codificar = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=10) 
    codificar.update({"exp": expire})
    encoded_jwt = pyjwt.encode(codificar, SECRET_KEY, algorithm=HASH_ALGORITHM)
    return encoded_jwt

###################################



router = APIRouter(tags=["Usuarios"], prefix="/usuarios")


##################################
########### HASHING ##############
##################################

load_dotenv()  
# from config.settings import settings
# settings.SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY")
HASH_ALGORITHM = os.getenv("HASH_ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class LoginRequest(BaseModel):
    username: str
    password: str

####################################
######## REGISTRAR USUARIO #########
####################################
@router.post("/register")
def register_usuario(user_request: UsuarioRegistrar, session: Session = Depends(get_session)):
    password_hash = pwd_context.hash(user_request.password)
    nuevo_usuario = Usuario(
        username=user_request.username,
        password=password_hash,  
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
############## Login ###############
####################################


@router.post("/login")
def login(login_request: LoginRequest, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.username == login_request.username)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not pwd_context.verify(login_request.password, usuario.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    usuario_accesos = session.exec(
        select(Acceso).join(UsuarioAcceso, UsuarioAcceso.acceso_id == Acceso.acceso_id)
        .where(UsuarioAcceso.usuario_id == usuario.username)
    ).all()

    expiracion_token = timedelta(hours=10)
    access_token = create_access_token(
        data={"sub": usuario.username},
        expires_delta=expiracion_token
    )

    return {
        "message": "Login Exitoso",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": usuario.username,
            "display_name": usuario.display_name,
            "email": usuario.email,
            "accesos": [acceso.nombre for acceso in usuario_accesos]
        }
    }



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
    usuario = session.get(Usuario, username)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_roles = session.exec(
        select(Rol).join(UsuarioRol, UsuarioRol.rol_id == Rol.rol_id)
        .where(UsuarioRol.usuario_id == username)
    ).all()

    usuario_accesos = session.exec(
        select(Acceso).join(UsuarioAcceso, UsuarioAcceso.acceso_id == Acceso.acceso_id)
        .where(UsuarioAcceso.usuario_id == username)
    ).all()

    return UsuarioRolesAccesos(usuario=usuario, roles=usuario_roles, accesos=usuario_accesos)

class UserBase(SQLModel):
    display_name: str
    email: str

class UsuarioUpdateSchema(UserBase):
    display_name: str | None = None
    email: str | None = None

class UsuarioReadSchema(UserBase):
    username: str

@router.patch("/{username}", response_model=UsuarioReadSchema)
def update_usuario(session: SessionDependency, username: str, user: UsuarioUpdateSchema):
    usuario = session.get(Usuario, username)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_dict = user.model_dump(exclude_unset=True)
    usuario.sqlmodel_update(update_dict)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario