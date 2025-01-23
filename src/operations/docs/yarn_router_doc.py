from src.core.schemas import CreatedObjectResponse, ItemIsUpdatableSchema
from src.core.utils import (
    generate_doc,
    generate_response_content,
    generate_response_doc,
)
from src.operations.failures import YARN_UPDATE_FAILURE_DUE_TO_FABRIC_RECIPE_IN_USE


class YarnRouterDocumentation:
    @staticmethod
    def create_yarn() -> dict:
        description = """
Este `endpoint` permite crear un nuevo hilado en la base de datos.

Tener en cuenta los siguientes endpoints para la creación del nuevo hilado:
- `GET /yarn-counts`: Retorna una lista de **titulos de hilado** disponibles.
- `GET /spinning-methods`: Retorna una lista de **acabados de hilado** disponibles.
- `GET /yarn-manufacturing-sites`: Retorna una lista de **lugares de fabricación de hilado** disponibles.
- `GET /yarn-distinctions`: Retorna una lista de **distinciones de hilado** disponibles.
- `GET /mecsa-colors`: Retorna una lista de **colores** disponibles.
"""
        message = "El hilado ha sido creado con éxito."
        return generate_doc(
            response_model=CreatedObjectResponse,
            description=description,
            responses=generate_response_doc(
                status_code=200,
                content=generate_response_content(
                    examples=CreatedObjectResponse(message=message).model_dump()
                ),
            ),
        )

    @staticmethod
    def check_is_yarn_updatable() -> dict:
        description = """
Este `endpoint` permite verificar si un hilado puede ser actualizado y qué tipo de actualización es posible:

- **Actualización completa**:
    En el caso de ser una actualización completa, se podrán modificar **cualquier atributo** del hilado sin \
    restricciones.

- **Actualización parcial**:
    En el caso de ser una actualización parcial, **únicamente** podrá editarse la **descripción** del hilado. \
    Esto suele ocurrir cuando el hilado está siendo utilizado, el motivo específico se indicará en el campo \
    `message`.

- **Actualización no permitida**:
    No se podrá realizar ninguna actualización si el hilado se encuentra **desactivado**. Para actualizar un \
    hilado desactivado, deberá ser reactivado previamente.

- **Recomendación:**
    Siempre llama a este `endpoint` antes de intentar modificar un hilado para determinar si es posible la \
    actualización.
"""
        fields = ["description"]
        message_n2 = (
            YARN_UPDATE_FAILURE_DUE_TO_FABRIC_RECIPE_IN_USE.error.detail
            + " Solo se podrá editar la descripción."
        )

        examples = {
            "Ejemplo N°1": {
                "value": ItemIsUpdatableSchema(
                    message="Es posible realizar una actualización completa del hilado especificado.",
                ).model_dump()
            },
            "Ejemplo N°2": {
                "value": ItemIsUpdatableSchema(
                    is_partial=True,
                    message=message_n2,
                    fields=fields,
                ).model_dump()
            },
        }

        return generate_doc(
            response_model=ItemIsUpdatableSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200, content=generate_response_content(examples=examples)
            ),
        )
