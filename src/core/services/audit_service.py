import json
from functools import wraps

from fastapi import Depends, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db, get_promec_db
from src.core.result import Failure

from ...security.services.token_service import TokenService


class AuditService:
    def __init__(
        self,
        promec_db: AsyncSession = None,
        db: AsyncSession = None,
    ):
        self.promec_db = promec_db
        self.db = db

    @staticmethod
    def audit_action_log():
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("request")
                db: AsyncSession = kwargs.get("db")

                access_token = request.cookies.get("access_token")
                user_id: int | None = None
                endpoint_name = getattr(request.scope.get("route"), "name", None)
                action = request.method
                if access_token:
                    token_service = TokenService(db=db)

                    verification_result = token_service.verify_access_token(
                        token=access_token
                    )
                    if verification_result.is_failure:
                        user_id = None
                    else:
                        user_id = verification_result.value.user_id

                request_data: dict | None = None

                try:
                    request_data = await request.json()
                except Exception:
                    request_data = None

                try:
                    response = await func(*args, **kwargs)
                except Exception as exc:
                    detail = getattr(exc, "detail", None)
                    print("AUDIT: Excepción custom capturada:", exc)
                    print("Detalle:", detail)
                    raise exc

                # except Exception as e:
                #     if isinstance(e, dict):
                #         error_json = json.dumps(e)
                #     else:
                #     # Si es un str o cualquier otra cosa
                #        error_json = str(e)
                #
                #     print(error_json)
                #     raise e

                response_data: dict | None = None

                try:
                    encoded = jsonable_encoder(response)
                    response_data = json.dumps(encoded)  # string JSON
                except Exception:
                    response_data = str(response)

                print("asdasdasdasdasdasdasd")
                print(endpoint_name, user_id, action, request_data, response_data)

                return response

            return wrapper

        return decorator
