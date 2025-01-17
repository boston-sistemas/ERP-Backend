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


DATA_TYPES = {
    DataType.STRING.value: {
        "id": DataType.STRING.value,
        "name": "Cadena de texto",
        "description": "Secuencia de caracteres, como: Hola Mundo",
    },
    DataType.INTEGER.value: {
        "id": DataType.INTEGER.value,
        "name": "Entero",
        "description": "Número sin decimales, como: 200",
    },
    DataType.FLOAT.value: {
        "id": DataType.FLOAT.value,
        "name": "Flotante",
        "description": "Número con decimales, como: 3.14",
    },
    DataType.BOOLEAN.value: {
        "id": DataType.BOOLEAN.value,
        "name": "Booleano",
        "description": "Valor lógico: true o false",
    },
    DataType.DATE.value: {
        "id": DataType.DATE.value,
        "name": "Fecha",
        "description": "Fecha en formato: DD/MM/YYYY",
    },
    DataType.DATETIME.value: {
        "id": DataType.DATETIME.value,
        "name": "Fecha y hora",
        "description": "Fecha y hora en formato: DD/MM/YYYY HH:MM:SS",
    },
    DataType.LIST_STRING.value: {
        "id": DataType.LIST_STRING.value,
        "name": "Lista de cadenas de texto",
        "description": "Colección de cadenas, como: Boston,Sweet Cotton,Ropa Interior",
    },
}


class DataTypeListSchema(CustomBaseModel):
    data_types: list[dict[str, str]] = list(DATA_TYPES.values())


class FiberCategoriesSchema(CustomBaseModel):
    fiber_categories: list["ParameterValueSchema"]


class UserPasswordPolicySchema(CustomBaseModel):
    min_length: int = 6
    min_uppercase: int = 1
    min_lowercase: int = 1
    min_digits: int = 1
    min_symbols: int = 1
    validity_days: int = 30
    history_size: int = 3


class SpinningMethodsSchema(CustomBaseModel):
    spinning_methods: list["ParameterValueSchema"]


class FabricTypesSchema(CustomBaseModel):
    fabric_types: list["ParameterValueSchema"]


class ServiceOrderStatusSchema(CustomBaseModel):
    service_order_status: list["ParameterValueSchema"]


class FiberDenominationsSchema(CustomBaseModel):
    fiber_denominations: list["ParameterValueSchema"]


from .parameter_schema import ParameterValueSchema  # noqa: E402

FiberCategoriesSchema.model_rebuild()
