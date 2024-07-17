from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.security.schemas import (
    LoginForm,
    LoginResponse,
    LoginWithTokenForm,
    LogoutResponse,
    RefreshResponse,
    SendTokenResponse,
)
from src.security.services import AuthService

router = APIRouter(tags=["Seguridad - Auth"], prefix="/auth")


def set_tokens_in_cookies(
    response: Response,
    access_token: str,
    access_token_expiration_at: datetime,
    refresh_token: str | None = None,
    refresh_token_expiration_at: datetime | None = None,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        expires=access_token_expiration_at.astimezone(UTC),
        secure=False if settings.DEBUG else True,
        samesite="lax",
    )

    if refresh_token is None:
        return

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=refresh_token_expiration_at.astimezone(UTC),
        secure=False if settings.DEBUG else True,
        samesite="lax",
    )


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

    set_tokens_in_cookies(
        response,
        result.access_token,
        result.access_token_expiration_at,
        result.refresh_token_at,
        result.refresh_token_expiration_at,
    )

    return result


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_access_token(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    refresh_token = request.cookies.get("refresh_token")
    refresh_result = await auth_service.refresh_access_token(refresh_token)
    if refresh_result.is_failure:
        raise refresh_result.error

    result = refresh_result.value
    set_tokens_in_cookies(
        response, result.access_token, result.access_token_expiration_at
    )

    return result


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
