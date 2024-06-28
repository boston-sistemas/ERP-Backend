from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.orm import joinedload

from src.core.database import SessionDependency
from src.security.cruds import crud_sesion, crud_usuario
from src.security.models import Sesion, Usuario
from src.security.schemas import LoginForm, UsuarioSimpleSchema
from src.security.services.auth_services import AuthService
from src.security.utils import (
    authenticate_user,
    calculate_session_expiration,
    create_access_token,
    create_refresh_token,
    get_valid_acceses,
    validate_sesion,
    validate_user_status,
    verify_token,
)

router = APIRouter(tags=["Seguridad - Auth"], prefix="/auth")


@router.post("/login")
def login(
    request: Request, response: Response, form: LoginForm, session: SessionDependency
):
    session = AuthService(session)
    usuario = session.read_model_by_parameter(
        Usuario, Usuario.username == form.username
    )
    is_valid_user = validate_user_status(usuario) and authenticate_user(
        usuario, form.password
    )

    if not is_valid_user:
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
    session.create_session(current_sesion)

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
        "usuario": UsuarioSimpleSchema.from_orm(usuario),
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_access_token(request: Request, session: SessionDependency):
    session = AuthService(session)
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing."
        )

    claims = verify_token(refresh_token)
    current_sesion = session.read_model_by_parameter(
        Sesion, Sesion.sesion_id == claims["sid"]
    )

    if not current_sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )

    if not validate_sesion(current_sesion):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied"
        )

    access_token = create_access_token(
        payload={
            "sub": current_sesion.usuario.usuario_id,
            "username": current_sesion.usuario.username,
            "accesos": get_valid_acceses(current_sesion.usuario),
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(request: Request, response: Response, session: SessionDependency):
    session = AuthService(session)
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing."
        )

    claims = verify_token(refresh_token)

    current_sesion = session.read_model_by_parameter(
        Sesion, Sesion.sesion_id == claims["sid"]
    )

    if not current_sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )

    session.update_session(current_sesion, {"not_after": datetime.now()})

    response.delete_cookie(key="refresh_token")
    return {"message": "Sesión cerrada exitosamente"}
