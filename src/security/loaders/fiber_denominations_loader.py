from src.operations.failures import (
    DENOMINATION_DISABLED_FIBER_VALIDATION_FAILURE,
    DENOMINATION_NOT_FOUND_FIBER_VALIDATION_FAILURE,
)

from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class FiberDenominations(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.FIBER_DENOMINATION_PARAM_CATEGORY_ID,
):
    not_found_failure = DENOMINATION_NOT_FOUND_FIBER_VALIDATION_FAILURE
    disabled_failure = DENOMINATION_DISABLED_FIBER_VALIDATION_FAILURE
