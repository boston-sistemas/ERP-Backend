import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent) + "/"


class ProjectBaseSettings(BaseSettings):
    PROJECT_DIR: str = BASE_DIR + "src/"
    ASSETS_DIR: str = PROJECT_DIR + "core/assets/"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR + ".env",
        env_ignore_empty=True,
        extra="ignore",
    )


class ProjectSettings(ProjectBaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MECSA - API"
    ENVIRONMENT: str
    DEBUG: bool = True
    ALLOWED_ORIGINS: list[str]

    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    PROMEC_DATABASE_URL: str
    PROMEC_DATABASE_URL_ASYNC: str

    SECRET_KEY: str
    SIGNING_ALGORITHM: str

    RESEND_API_KEY: str
    MAILHOG_HOSTNAME: str
    MAILHOG_PORT: int
    SENDER_NAME: str
    SENDER_EMAIL: str
    FRONTEND_URL: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sys.path.append(BASE_DIR)


settings = ProjectSettings()

if __name__ == "__main__":
    print(settings.model_dump())
