from src.core.utils import (
    generate_doc,
    generate_response_content,
    generate_response_doc,
)


class RateRouterDocumentation:
    @staticmethod
    def create_service_rate() -> dict:
        description = """
Este `endpoint` permite crear una nueva tarifa de servicio en la base de datos.

- `GET /

"""
