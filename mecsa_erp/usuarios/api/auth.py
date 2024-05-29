from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from config.database import SessionDependency

from helpers.crud import CRUD
from mecsa_erp.usuarios.models import Sesion, Usuario
from mecsa_erp.usuarios.schemas.auth import LoginForm
from mecsa_erp.usuarios.schemas.usuario import UsuarioSimpleSchema
from mecsa_erp.usuarios.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_HOURS,
    authenticate_user,
    create_token,
    get_valid_acceses,
    verify_token,
)

from mecsa_erp.usuarios.crud.usuario import crud_usuario

crud_sesion = CRUD[Sesion, Sesion](Sesion)

router = APIRouter(tags=["Auth"], prefix="/auth")

router.app


@router.post("/login")
def login(request: Request, form: LoginForm, session: SessionDependency):
    usuario = crud_usuario.get(session, Usuario.username == form.username)

    authenticated = authenticate_user(usuario, form.password)

    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales no válidas"
        )

    iat = datetime.now()
    access_token_expiration = iat + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    sesion_expiration = refresh_token_expiration = iat + timedelta(
        hours=REFRESH_TOKEN_EXPIRE_HOURS
    )

    current_sesion = Sesion(
        usuario_id=usuario.usuario_id,
        not_after=sesion_expiration,
        ip=request.client.host,
    )
    crud_sesion.create(session, current_sesion)

    access_token = create_token(
        payload={
            "aud": "authenticated",
            "iat": iat,
            "exp": access_token_expiration,
            "sub": usuario.username,
            "accesos": get_valid_acceses(usuario),
        }
    )

    refresh_token = create_token(
        payload={
            "iat": iat,
            "sid": str(current_sesion.sesion_id),
            "exp": refresh_token_expiration,
            "sub": usuario.username,
        }
    )

    response = JSONResponse(
        status_code=200,
        content={
            "message": "Inicio de sesión exitoso",
            "usuario": UsuarioSimpleSchema.model_validate(usuario).model_dump(),
            "access_token": access_token,
        },
    )

    response.set_cookie(
        key="refresh_token",
        value=f"{refresh_token}",
        httponly=True,
        expires=int(timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS).total_seconds()),
        secure=False,  # Cambiar a True en producción
        samesite="Lax",
    )

    return response


@router.post("/refresh")
def refresh_access_token(request: Request, session: SessionDependency):
    pass


@router.post("/logout")
def logout(request: Request, response: Response, session: SessionDependency):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing."
        )

    claims = verify_token(refresh_token)

    current_sesion = crud_sesion.get_by_pk_or_404(session, claims["sid"])
    current_sesion.not_after = datetime.now()
    session.add(current_sesion)
    session.commit()

    response.delete_cookie(key="refresh_token")
    return {"message": "Sesión cerrada exitosamente"}
