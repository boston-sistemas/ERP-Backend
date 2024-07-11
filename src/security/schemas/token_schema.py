from pydantic import BaseModel


class AccessTokenData(BaseModel):
    user_id: int
    accesos: list[str]


class RefreshTokenData(BaseModel):
    user_id: int
    sesion_id: str
