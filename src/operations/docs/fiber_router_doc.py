from src.core.schemas import ItemIsUpdatableSchema
from src.operations.failures import FIBER_UPDATE_FAILURE_DUE_TO_YARN_RECIPE_IN_USE


class FiberRouterDocumentation:
    @staticmethod
    def check_is_fiber_updatable() -> dict:
        description = """
**Actualmente no es posible realizar una actualización parcial para alguna fibra.**

En caso de que se determine que una fibra pueda ser actualizada, se podrá actualizar cualquier atributo.

- **Recomendación:** Llama a este `endpoint` antes de intentar editar una fibra para verificar si se puede realizar la actualización.
- **Nota:** Si no es posible actualizar una fibra, el motivo se indicará en el campo `message`.
"""
        example_n1 = ItemIsUpdatableSchema(
            message="Es posible realizar la actualización de la fibra especificada.",
        ).model_dump()
        example_n2 = ItemIsUpdatableSchema(
            failure=FIBER_UPDATE_FAILURE_DUE_TO_YARN_RECIPE_IN_USE
        ).model_dump()

        return {
            "description": description,
            "response_model": ItemIsUpdatableSchema,
            "responses": {
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "examples": {
                                "Ejemplo N°1": {"value": example_n1},
                                "Ejemplo N°2": {"value": example_n2},
                            }
                        }
                    },
                }
            },
        }
