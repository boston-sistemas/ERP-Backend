from datetime import timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from config.database import SessionDependency
from mecsa_erp.usuarios.schemas.auth import LoginForm
from mecsa_erp.usuarios.schemas.usuario import UsuarioSimpleSchema
from mecsa_erp.usuarios.security import create_access_token, verify_password

from .usuario import crud_usuario

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/login")
def login(session: SessionDependency, form: LoginForm):
    usuario = crud_usuario.get_by_pk(session, form.username)

    password_correct = (
        False if usuario is None else verify_password(form.password, usuario.password)
    )

    if not password_correct:
        raise HTTPException(status_code=401, detail="Usuario o contraseña no válidos")

    expiracion_token = timedelta(hours=10)
    data = UsuarioSimpleSchema.model_validate(usuario).model_dump()
    access_token = create_access_token(data=data, expires_delta=expiracion_token)

    response = JSONResponse(
        status_code=200,
        content={
            "message": "Login Exitoso",
            "usuario": data,
        },
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=int(expiracion_token.total_seconds()),
        expires=int(expiracion_token.total_seconds()),
        secure=False,  # Cambiar a True en producción
        samesite="Lax",
    )

    return response
