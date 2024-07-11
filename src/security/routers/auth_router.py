from datetime import UTC

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.schemas import (
    LoginForm,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    LoginWithTokenForm,
    SendTokenResponse,
)
from src.security.services import AuthService

router = APIRouter(tags=["Seguridad - Auth"], prefix="/auth")


@router.post("/send-token", response_model=SendTokenResponse)
async def send_token(
    form: LoginForm,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    send_token_result = await auth_service.send_auth_token(form)
    
    if send_token_result.is_success:
        return send_token_result.value
    raise send_token_result.error


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    response: Response,
    form: LoginWithTokenForm,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    login_result = await auth_service.login(form, ip=request.client.host)
    if login_result.is_failure:
        raise login_result.error

    result = login_result.value
    if result.refresh_token is not None:
        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            expires=result.refresh_token_expiration.astimezone(UTC),
            secure=False,  # TODO: Cambiar a True en producción
            samesite="Lax",
        )

    return result


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_access_token(request: Request, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)

    refresh_token = request.cookies.get("refresh_token")
    refresh_result = await auth_service.refresh_access_token(refresh_token)
    if refresh_result.is_failure:
        raise refresh_result.error

    return refresh_result.value


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    refresh_token = request.cookies.get("refresh_token")
    logout_result = await auth_service.logout(refresh_token)
    if logout_result.is_failure:
        raise logout_result.error

    response.delete_cookie(key="refresh_token")
    return logout_result.value
