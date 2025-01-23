from src.operations.failures import (
    YARN_DISTINCTION_DISABLED_FAILURE,
    YARN_DISTINCTION_NO_FOUND_FAILURE,
)

from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class YarnDistinctions(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.YARN_DISTINCTION_PARAM_CATEGORY_ID,
):
    not_found_failure = YARN_DISTINCTION_NO_FOUND_FAILURE
    disabled_failure = YARN_DISTINCTION_DISABLED_FAILURE
