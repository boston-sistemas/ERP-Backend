from src.operations.failures import (
    SPINNING_METHOD_DISABLED_YARN_VALIDATION_FAILURE,
    SPINNING_METHOD_NOT_FOUND_YARN_VALIDATION_FAILURE,
)

from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class SpinningMethods(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.SPINNING_METHOD_PARAM_CATEGORY_ID,
):
    not_found_failure = SPINNING_METHOD_NOT_FOUND_YARN_VALIDATION_FAILURE
    disabled_failure = SPINNING_METHOD_DISABLED_YARN_VALIDATION_FAILURE
