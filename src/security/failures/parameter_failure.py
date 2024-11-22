from src.core.exceptions import NotFoundException, UnprocessableEntityException
from src.core.result import Failure

PARAMETER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="Parametro no encontrado")
)

PARAMETER_CATEGORY_NOT_FOUND_WHEN_CREATING_FAILURE = Failure(
    NotFoundException(
        detail="Categoría de Parámetro no encontrado. Parámetro no creado."
    )
)


def PARAMETER_VALUE_CONVERSION_FAILURE(value: str):
    return Failure(
        UnprocessableEntityException(
            detail=f"No se pudo convertir el valor: '{value}'."
        )
    )


def PARAMETER_VALUE_CONVERSION_TO_INT_FAILURE(value: str):
    return Failure(
        UnprocessableEntityException(
            detail=f"No se puede convertir '{value}' a un entero."
        )
    )


def PARAMETER_VALUE_CONVERSION_TO_FLOAT_FAILURE(value: str):
    return Failure(
        UnprocessableEntityException(
            detail=f"No se puede convertir '{value}' a un número decimal."
        )
    )


def PARAMETER_VALUE_CONVERSION_TO_DATE_FAILURE(value: str):
    return Failure(
        UnprocessableEntityException(
            detail=f"No es una fecha válida '{value}'. Formato esperado: DD/MM/YYYY."
        )
    )


def PARAMETER_VALUE_CONVERSION_TO_DATETIME_FAILURE(value: str):
    return Failure(
        UnprocessableEntityException(
            detail=f"No es una fecha y hora válida '{value}'. Formato esperado: DD/MM/YYYY HH:MM:SS."
        )
    )


def PARAMETER_VALUE_CONVERSION_TO_BOOLEAN_FAILURE(value: str):
    return Failure(
        UnprocessableEntityException(
            detail=f"No es un valor booleano válido '{value}'. Se esperaba: true o false."
        )
    )
