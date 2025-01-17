from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class FiberDenominations(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.FIBER_DENOMINATION_PARAM_CATEGORY_ID,
):
    pass
