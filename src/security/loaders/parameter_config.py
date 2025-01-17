from pydantic_settings import SettingsConfigDict

from src.core.config import BASE_DIR, ProjectBaseSettings


class ParameterSettings(ProjectBaseSettings):
    model_config = SettingsConfigDict(
        env_file=[BASE_DIR + ".params.env.local", BASE_DIR + ".params.env"],
        env_ignore_empty=True,
        extra="ignore",
    )

    FIBER_CATEGORY_PARAM_CATEGORY_ID: int

    MIN_PASSWORD_LENGTH_PARAM_ID: int
    MIN_PASSWORD_UPPERCASE_PARAM_ID: int
    MIN_PASSWORD_LOWERCASE_PARAM_ID: int
    MIN_PASSWORD_DIGITS_PARAM_ID: int
    MIN_PASSWORD_SYMBOLS_PARAM_ID: int
    PASSWORD_VALIDITY_DAYS_PARAM_ID: int
    PASSWORD_HISTORY_SIZE_PARAM_ID: int
    SPINNING_METHOD_PARAM_CATEGORY_ID: int
    FABRIC_TYPE_PARAM_CATEGORY_ID: int
    JERSEY_FABRIC_TYPE_ID: int
    RIB_BVD_FABRIC_TYPE_ID: int
    SERVICE_ORDER_CATEGORY_STATUS_ID: int
    FIBER_DENOMINATION_PARAM_CATEGORY_ID: int


param_settings = ParameterSettings()
