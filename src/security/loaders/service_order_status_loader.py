from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings


class ServiceOrderStatus(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.SERVICE_ORDER_CATEGORY_STATUS_ID,
):
    pass
