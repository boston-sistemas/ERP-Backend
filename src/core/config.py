import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectSettings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent) + "/"
    PROJECT_DIR: str = BASE_DIR + "src/"
    ASSETS_DIR: str = PROJECT_DIR + "core/assets/"
    ENV_FILE: str = BASE_DIR + ".env"
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_ignore_empty=True, extra="ignore"
    )

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
        sys.path.append(self.BASE_DIR)


settings = ProjectSettings()

if __name__ == "__main__":
    print(settings.model_dump())
