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
    access_token_expiration: datetime,
    refresh_token: str | None = None,
    refresh_token_expiration: datetime | None = None,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        expires=access_token_expiration.astimezone(UTC),
        secure=False if settings.DEBUG else True,
        samesite="Lax",
    )

    if refresh_token is None:
        return

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=refresh_token_expiration.astimezone(UTC),
        secure=False if settings.DEBUG else True,
        samesite="Lax",
    )


@router.post("/pruebas")
async def pruebas(
    db: AsyncSession = Depends(get_db),
):
    data = {
        "semana": 21,
        "from": "TEXTILES ROCA 29 S.A.C.",
        "email_to": ["practicante.sistemas@boston.com.pe"],
        "to": "Tricot Fine",
        "ignore_columns_pdf": ["Tejeduría", "Tintorería"],
        "title": [
            "Partida",
            "Tejeduría",
            "Hilanderia",
            "OS",
            "Tejido",
            "Ancho",
            "Rollos",
            "Peso",
            "Tintorería",
            "Color",
        ],
        # 'title': ['Partida', 'Hilanderia', 'OS', 'Tejido', 'Ancho', 'Rollos', 'Peso', 'Color'],
        "values": [
            [
                "1",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
            [
                "1",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
            [
                "2",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
            [
                "1",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
            [
                "1",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
            [
                "2",
                "textiles roca 29 s.a.c.",
                "san ignacio",
                "tri1749",
                "jersey llano 30/1 melange 80/20",
                "90",
                "3",
                "60",
                "color y textura",
                "lavado",
            ],
            [
                "3",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
            [
                "4",
                "TEXTILES ROCA 29 S.A.C.",
                "SAN IGNACIO",
                "TRI1749",
                "Jersey Llano 30/1 Melange 80/20",
                "90",
                "3",
                "60",
                "Color y Textura",
                "Lavado",
            ],
        ],
        "comments": "Comentarios de la programación de la semana 21 de 2021, se ha realizado la programación de los tejidos de la empresa Tricot Fine S.A. para ser enviados a la empresa Tricot Fine para el proceso de tintorería. Se ha programado un total de 4 partidas, 2 de ancho 90 y 2 de ancho 80, con un total de 52 rollos y 1040 kilogramos de peso .",
    }

    auth_service = AuthService(db)
    send = await auth_service.send_email_pdf_table(data)

    print(send)

    return {"message": "Pruebas de autenticación"}


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
        result.access_token_expiration,
        result.refresh_token,
        result.refresh_token_expiration,
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
    set_tokens_in_cookies(response, result.access_token, result.access_token_expiration)

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
