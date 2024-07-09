from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class EspecialidadEmpresaFailures:
    _ESPECIALIDAD_NOT_FOUND_ERROR = NotFoundException(
        detail="Especialidad de empresa no encontrada."
    )

    ESPECIALIDAD_NOT_FOUND_FAILURE = Failure(_ESPECIALIDAD_NOT_FOUND_ERROR)
