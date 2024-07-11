from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
)
from src.core.result import Failure


class UserFailures:
    _USER_NOT_FOUND_ERROR = NotFoundException(detail="Usuario no encontrado")
    _USER_ROLE_NOT_FOUND_ERROR = NotFoundException(
        detail="El usuario no cuenta con el rol"
    )
    _USER_HAS_ROLE_WHEN_ADDING_ERROR = DuplicateValueException(
        detail="El usuario ya cuenta con el rol. No se añadieron los roles especificados"
    )
    _USER_MISSING_ROLE_WHEN_DELETING_ERROR = NotFoundException(
        detail="El usuario no cuenta con el rol. No se eliminaron los roles especificados"
    )
    _ROLE_NOT_FOUND_WHEN_CREATING_ERROR = NotFoundException(
        detail="Rol no encontrado. Usuario no creado"
    )
    _ROLE_NOT_FOUND_WHEN_ADDING_ERROR = NotFoundException(
        detail="Rol no encontrado. No se añadieron los roles especificados"
    )
    _ROLE_NOT_FOUND_WHEN_DELETING_ERROR = NotFoundException(
        detail="Rol no encontrado. No se eliminaron los roles especificados"
    )

    USER_NOT_FOUND_FAILURE = Failure(_USER_NOT_FOUND_ERROR)
    USER_ROLE_NOT_FOUND_FAILURE = Failure(_USER_ROLE_NOT_FOUND_ERROR)
    USER_HAS_ROLE_WHEN_ADDING_FAILURE = Failure(_USER_HAS_ROLE_WHEN_ADDING_ERROR)
    USER_MISSING_ROLE_WHEN_DELETING_FAILURE = Failure(
        _USER_MISSING_ROLE_WHEN_DELETING_ERROR
    )
    ROLE_NOT_FOUND_WHEN_CREATING_FAILURE = Failure(_ROLE_NOT_FOUND_WHEN_CREATING_ERROR)
    ROLE_NOT_FOUND_WHEN_ADDING_FAILURE = Failure(_ROLE_NOT_FOUND_WHEN_ADDING_ERROR)
    ROLE_NOT_FOUND_WHEN_DELETING_FAILURE = Failure(_ROLE_NOT_FOUND_WHEN_DELETING_ERROR)

    @staticmethod
    def USERNAME_ALREADY_EXISTS_FAILURE(username: str):
        _ERROR = DuplicateValueException(f"El username {username} ya existe")
        return Failure(_ERROR)
