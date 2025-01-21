from src.operations.failures import (
    YARN_COUNT_DISABLED_FAILURE,
    YARN_COUNT_NO_FOUND_FAILURE,
)

from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class YarnCounts(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.YARN_COUNT_PARAM_CATEGORY_ID,
):
    not_found_failure = YARN_COUNT_NO_FOUND_FAILURE
    disabled_failure = YARN_COUNT_DISABLED_FAILURE
