from enum import Enum

from src.core.schemas import CustomBaseModel


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    LIST_STRING = "list_string"


class DataTypeListSchema(CustomBaseModel):
    data_types: list[dict[str, str]] = [
        {
            "id": DataType.STRING.value,
            "name": "Cadena de texto",
            "description": "Secuencia de caracteres, como: Hola Mundo",
        },
        {
            "id": DataType.INTEGER.value,
            "name": "Entero",
            "description": "Número sin decimales, como: 200",
        },
        {
            "id": DataType.FLOAT.value,
            "name": "Flotante",
            "description": "Número con decimales, como: 3.14",
        },
        {
            "id": DataType.BOOLEAN.value,
            "name": "Booleano",
            "description": "Valor lógico: true o false",
        },
        {
            "id": DataType.DATE.value,
            "name": "Fecha",
            "description": "Fecha en formato: DD/MM/YYYY",
        },
        {
            "id": DataType.DATETIME.value,
            "name": "Fecha y hora",
            "description": "Fecha y hora en formato: DD/MM/YYYY HH:MM:SS",
        },
        {
            "id": DataType.LIST_STRING.value,
            "name": "Lista de cadenas de texto",
            "description": "Colección de cadenas, como: Boston,Sweet Cotton,Ropa Interior",
        },
    ]
