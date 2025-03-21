from src.core.schemas import CreatedObjectResponse, ItemIsUpdatableSchema
from src.core.utils import (
    generate_doc,
    generate_response_content,
    generate_response_doc,
)

from .rate_schema import (
    RateCreateSchema,
    RateFilterParams,
    RateListSchema,
    RateSchema,
    RateUpdateSchema,
)


class RateRouterDocumentation:
    @staticmethod
    def read_service_rates() -> dict:
        description = """
Este `endpoint` permite obtener una lista paginada de tarifas de servicios registradas en el sistema.

Cada tarifa representa un costo asociado a un servicio en función de la tela (`fabric_id`), proveedor (`supplier_id`) y período.

**Filtros disponibles:**
- `period`, `month_number`: año y mes de la tarifa
- `serial_code`: código del servicio
- `supplier_ids`: proveedores
- `fabric_ids`: telas
- `currency`: moneda (`0` = dólares, `1` = soles)
- `page`: número de página para paginación
"""

        example = {
            "Ejemplo #1": {
                "value": RateListSchema(
                    service_rates=[
                        RateSchema(
                            rate_id=100102,
                            serial_code="003",
                            supplier_id="P00323",
                            currency=0,
                            fabric_id="100100100124",
                            rate=0.7,
                            period=2025,
                            month_number=3,
                            currency_name="Dólares",
                        ),
                        RateSchema(
                            rate_id=100101,
                            serial_code="003",
                            supplier_id="P00323",
                            fabric_id="100100100123",
                            currency=0,
                            rate=0.84,
                            period=2025,
                            month_number=3,
                            currency_name="Dólares",
                        ),
                    ]
                ).model_dump()
            }
        }

        return generate_doc(
            response_model=RateListSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200,
                content=generate_response_content(examples=example),
            ),
        )

    @staticmethod
    def read_service_rate() -> dict:
        description = """
Este `endpoint` permite obtener los detalles de una tarifa de servicio en particular.

Para obtener los detalles de una tarifa, se debe proporcionar el `rate_id` de la tarifa.
"""

        example = {
            "Ejemplo #1": {
                "value": RateSchema(
                    rate_id=100102,
                    serial_code="003",
                    supplier_id="P00323",
                    fabric_id="100100100124",
                    currency=0,
                    rate=0.7,
                    period=2025,
                    month_number=3,
                    currency_name="Dólares",
                ).model_dump()
            }
        }

        return generate_doc(
            response_model=RateSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200,
                content=generate_response_content(examples=example),
            ),
        )

    @staticmethod
    def create_service_rate() -> dict:
        description = """
Este `endpoint` permite registrar una nueva tarifa de servicio en la base de datos.

Para la creación de tarifas se tiene en cuenta las siguientes validaciones:
- El proveedor (`supplier_id`) debe tener asignado el servicio (`serial_code`).
- La tela (`fabric_id`) debe existir en la base de datos.
"""

        example = {
            "Ejemplo #1": {
                "value": RateSchema(
                    rate_id=100104,
                    serial_code="003",
                    supplier_id="P00323",
                    fabric_id="100100100124",
                    currency=0,
                    rate=0.7,
                    period=2025,
                    month_number=3,
                    currency_name="Dólares",
                ).model_dump()
            }
        }

        return generate_doc(
            response_model=RateSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200,
                content=generate_response_content(examples=example),
            ),
        )

    @staticmethod
    def update_service_rate() -> dict:
        description = """
Este `endpoint` permite actualizar una tarifa de servicio en la base de datos.

Se debe tener en cuenta que:
- La tarifa (`rate`) solo se puede modificar si la orden de servicio esté en estado: **Programada** o **Anulada**.
- **Recomendación**: Llama al endpoint `GET /{rate_id}/is-updatable` antes de intentar actualizar una tarifa para verificar si se puede realizar la actualización.
"""

        example = {
            "Ejemplo #1": {
                "value": RateSchema(
                    rate_id=100104,
                    serial_code="003",
                    supplier_id="P00323",
                    fabric_id="100100100124",
                    currency=0,
                    rate=0.84,
                    period=2025,
                    month_number=3,
                    currency_name="Dólares",
                ).model_dump()
            }
        }

        return generate_doc(
            response_model=RateSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200,
                content=generate_response_content(examples=example),
            ),
        )

    @staticmethod
    def is_updated_permission_service_rate() -> dict:
        description = """
Este `endpoint` permite verificar si una tarifa de servicio puede ser actualizada.

- **Recomendación**: Llama a este `endpoint` antes de intentar actualizar una tarifa para determinar si es posible la actualización.

"""
        example = {
            "Ejemplo #1": {
                "value": {
                    "updatable": True,
                    "message": "La tarifa especificada puede ser actualizada.",
                }
            },
            "Ejemplo #2": {
                "value": {
                    "updatable": False,
                    "message": "No se puede actualizar la tarifa especificada.",
                }
            },
        }

        return generate_doc(
            response_model=ItemIsUpdatableSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200,
                content=generate_response_content(examples=example),
            ),
        )
