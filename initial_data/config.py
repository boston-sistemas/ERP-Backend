import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent) + "/"
    ENV_FILE: str = BASE_DIR + ".env"
    model_config = SettingsConfigDict(
        env_file=[BASE_DIR + ".env", BASE_DIR + ".env.local"],
        env_ignore_empty=True,
        extra="ignore",
    )
    DATABASE_URL: str
    PROMEC_DATABASE_URL: str | None
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_USERNAME: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sys.path.append(self.BASE_DIR)


settings = Settings()


if __name__ == "__main__":
    print(settings.model_dump())