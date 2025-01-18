from src.operations.failures import (
    CATEGORY_DISABLED_FIBER_VALIDATION_FAILURE,
    CATEGORY_NOT_FOUND_FIBER_VALIDATION_FAILURE,
)

from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class FiberCategories(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.FIBER_CATEGORY_PARAM_CATEGORY_ID,
):
    not_found_failure = CATEGORY_NOT_FOUND_FIBER_VALIDATION_FAILURE
    disabled_failure = CATEGORY_DISABLED_FIBER_VALIDATION_FAILURE
