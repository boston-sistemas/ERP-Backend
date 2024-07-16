from fastapi import Cookie

from src.security.services import TokenService


def get_current_user_id(access_token: str = Cookie()):
    result = TokenService.verify_access_token(access_token)
    if result.is_failure:
        raise result.error

    return result.value.user_id
