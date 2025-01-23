from src.operations.failures import (
    YARN_MANUFACTURING_SITE_DISABLED_FAILURE,
    YARN_MANUFACTURING_SITE_NO_FOUND_FAILURE,
)

from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class YarnManufacturingSites(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.YARN_MANUFACTURING_SITE_PARAM_CATEGORY_ID,
):
    not_found_failure = YARN_MANUFACTURING_SITE_NO_FOUND_FAILURE
    disabled_failure = YARN_MANUFACTURING_SITE_DISABLED_FAILURE
