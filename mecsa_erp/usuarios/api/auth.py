from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException, Request, Response, status
import pytz

from config.database import SessionDependency
from helpers.crud import CRUD

from mecsa_erp.usuarios.models import Sesion, Usuario
from mecsa_erp.usuarios.schemas.auth import LoginForm
from mecsa_erp.usuarios.schemas.usuario import UsuarioSimpleSchema
from mecsa_erp.usuarios.security import (
    authenticate_user,
    calculate_session_expiration,
    create_access_token,
    create_refresh_token,
    get_valid_acceses,
    verify_token,
)
from mecsa_erp.usuarios.crud.usuario import crud_usuario

crud_sesion = CRUD[Sesion, Sesion](Sesion)

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/login")
def login(
    request: Request, response: Response, form: LoginForm, session: SessionDependency
):
    usuario = crud_usuario.get(session, Usuario.username == form.username)
    authenticated = authenticate_user(usuario, form.password)

    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales no válidas"
        )

    iat = datetime.now(UTC)

    session_expiration = calculate_session_expiration(iat)
    current_sesion = Sesion(
        usuario_id=usuario.usuario_id,
        not_after=session_expiration,
        ip=request.client.host,
    )
    crud_sesion.create(session, current_sesion)

    access_token = create_access_token(
        payload={
            "sub": usuario.usuario_id,
            "username": usuario.username,
            "accesos": get_valid_acceses(usuario),
        },
        iat=iat,
    )

    refresh_token = create_refresh_token(
        payload={
            "sid": str(current_sesion.sesion_id),
            "username": usuario.username,
        },
        iat=iat,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=session_expiration.astimezone(UTC),
        secure=False,  # Cambiar a True en producción
        samesite="Lax",
    )

    return {
        "message": "Inicio de sesión exitoso",
        "usuario": UsuarioSimpleSchema.model_validate(usuario),
        "access_token": access_token,
    }


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
    current_sesion.not_after = datetime.now(pytz.timezone("America/Lima"))
    session.add(current_sesion)
    session.commit()

    response.delete_cookie(key="refresh_token")
    return {"message": "Sesión cerrada exitosamente"}
