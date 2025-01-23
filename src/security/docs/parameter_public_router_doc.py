from src.core.utils import (
    generate_doc,
    generate_response_content,
    generate_response_doc,
)
from src.security.schemas import (
    SpinningMethodsSchema,
    YarnCountsSchema,
    YarnDistinctionsSchema,
    YarnManufacturingSitesSchema,
)


def generate_example(field: str, values: list):
    id = 1000
    return {field: [{"id": (id := id + 1), "value": value} for value in values]}


class ParameterPublicRouterDocumentation:
    @staticmethod
    def read_spinning_methods() -> dict:
        description = """
Devuelve una lista de **acabados de hilado** disponibles. Por ejemplo:

- `Peinado`
- `Cardado`
- `Open End`
"""
        example = generate_example(
            field="spinnningMethods", values=["Peinado", "Cardado", "Open End"]
        )
        return generate_doc(
            response_model=SpinningMethodsSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200, content=generate_response_content(examples=example)
            ),
        )

    @staticmethod
    def read_yarn_counts() -> dict:
        description = """
Devuelve una lista de **titulos de hilado** disponibles. Por ejemplo:

- `20 Dn`
- `40 Dn`
- `28/1 Ne`
- `30/1 Ne`
"""
        example = generate_example(
            field="yarnCounts", values=["20 Dn", "40 Dn", "28/1 Ne", "30/1 Ne"]
        )
        return generate_doc(
            response_model=YarnCountsSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200, content=generate_response_content(examples=example)
            ),
        )

    @staticmethod
    def read_yarn_manufacturing_sites() -> dict:
        description = """
Devuelve una lista de **lugares de fabricación de hilado** disponibles. Por ejemplo:

- `Vietnam - Thien`
"""
        example = generate_example(
            field="yarnManufacturingSites", values=["Vietnam - Thien Nam"]
        )
        return generate_doc(
            response_model=YarnManufacturingSitesSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200, content=generate_response_content(examples=example)
            ),
        )

    @staticmethod
    def read_yarn_distinctions() -> dict:
        description = """
Devuelve una lista de **distinciones de hilado** disponibles. Por ejemplo:

- `Libre de contaminación`
- `Contaminación controlada`

**Nota**: Cada distinción que se añada a un hilado, hace que dicho hilado sea único.
"""
        example = generate_example(
            field="yarnDistinctions",
            values=["Libre de contaminación", "Contaminación controlada"],
        )
        return generate_doc(
            response_model=YarnDistinctionsSchema,
            description=description,
            responses=generate_response_doc(
                status_code=200, content=generate_response_content(examples=example)
            ),
        )
