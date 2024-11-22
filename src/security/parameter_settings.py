from pydantic_settings import SettingsConfigDict

from src.core.config import BASE_DIR, ProjectBaseSettings


class ParameterSettings(ProjectBaseSettings):
    model_config = SettingsConfigDict(
        env_file=[BASE_DIR + ".params.env", BASE_DIR + ".params.env.local"],
        env_ignore_empty=True,
        extra="ignore",
    )

    FIBER_CATEGORY_PARAM_CATEGORY_ID: int


param_settings = ParameterSettings()
