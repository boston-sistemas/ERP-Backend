from src.core.exceptions import UnauthorizedException
from src.core.result import Failure


class AuthFailures:
    _INVALID_CREDENTIALS_ERROR = UnauthorizedException(
        detail="Credenciales no válidas."
    )

    INVALID_CREDENTIALS_FAILURE = Failure(_INVALID_CREDENTIALS_ERROR)

    UNAUTHORIZED_FAILURE = Failure(
        UnauthorizedException(detail="No esta autorizado para realizar esta acción.")
    )
