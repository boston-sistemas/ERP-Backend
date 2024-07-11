from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
)
from src.core.result import Failure


class RolFailures:
    _ROL_NOT_FOUND_ERROR = NotFoundException(detail="Rol no encontrado.")
    _ROL_ACCESO_NOT_FOUND_ERROR = NotFoundException(
        detail="El rol no cuenta con el acceso."
    )
    _ROL_HAS_ACCESO_WHEN_ADDING_ERROR = DuplicateValueException(
        detail="El rol ya cuenta con el acceso. No se añadieron los accesos especificados."
    )
    _ROL_MISSING_ACCESO_WHEN_DELETING_ERROR = NotFoundException(
        detail="El rol no cuenta con el acceso. No se eliminaron los accesos especificados."
    )
    _ACCESO_NOT_FOUND_WHEN_CREATING_ERROR = NotFoundException(
        detail="Acceso no encontrado. Rol no creado."
    )
    _ACCESO_NOT_FOUND_WHEN_ADDING_ERROR = NotFoundException(
        detail="Acceso no encontrado. No se añadieron los accesos especificados."
    )
    _ACCESO_NOT_FOUND_WHEN_DELETING_ERROR = NotFoundException(
        detail="Acceso no encontrado. No se eliminaron los accesos especificados."
    )

    ROL_NOT_FOUND_FAILURE = Failure(_ROL_NOT_FOUND_ERROR)
    ROL_ACCESO_NOT_FOUND_FAILURE = Failure(_ROL_ACCESO_NOT_FOUND_ERROR)
    ROL_HAS_ACCESO_WHEN_ADDING_FAILURE = Failure(_ROL_HAS_ACCESO_WHEN_ADDING_ERROR)
    ROL_MISSING_ACCESO_WHEN_DELETING_FAILURE = Failure(
        _ROL_MISSING_ACCESO_WHEN_DELETING_ERROR
    )
    ACCESO_NOT_FOUND_WHEN_CREATING_FAILURE = Failure(
        _ACCESO_NOT_FOUND_WHEN_CREATING_ERROR
    )
    ACCESO_NOT_FOUND_WHEN_ADDING_FAILURE = Failure(_ACCESO_NOT_FOUND_WHEN_ADDING_ERROR)
    ACCESO_NOT_FOUND_WHEN_DELETING_FAILURE = Failure(
        _ACCESO_NOT_FOUND_WHEN_DELETING_ERROR
    )

    @staticmethod
    def ROL_NAME_ALREADY_EXISTS_FAILURE(nombre: str):
        _ERROR = DuplicateValueException(f"Rol {nombre} ya existe.")
        return Failure(_ERROR)
