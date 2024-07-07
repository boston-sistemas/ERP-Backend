from src.core.exceptions import UnauthorizedException
from src.core.result import Failure


class TokenFailures:
    _INVALID_TOKEN_ERROR = UnauthorizedException(detail="Token inválido.")
    _INVALID_TOKEN_TYPE_ERROR = UnauthorizedException(detail="Token inválido.")
    _MISSING_REFRESH_TOKEN_ERROR = UnauthorizedException(
        detail="Refresh token missing."
    )
    _MISSING_ACCESS_TOKEN_ERROR = UnauthorizedException(detail="Access token missing.")

    INVALID_TOKEN_FAILURE = Failure(_INVALID_TOKEN_ERROR)
    INVALID_TOKEN_TYPE_FAILURE = Failure(_INVALID_TOKEN_TYPE_ERROR)
    MISSING_REFRESH_TOKEN_FAILURE = Failure(_MISSING_REFRESH_TOKEN_ERROR)
    MISSING_ACCESS_TOKEN_FAILURE = Failure(_MISSING_ACCESS_TOKEN_ERROR)
