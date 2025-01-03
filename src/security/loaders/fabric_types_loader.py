from .multi_parameter_loader_by_category import MultiParameterLoaderByCategory
from .parameter_config import param_settings
from .single_parameter_loader import SingleParameterLoader


class FabricTypes(
    MultiParameterLoaderByCategory,
    param_category_id=param_settings.FABRIC_TYPE_PARAM_CATEGORY_ID,
):
    pass


class JerseyFabric(SingleParameterLoader, id=param_settings.JERSEY_FABRIC_TYPE_ID):
    pass


class RibBvdFabric(SingleParameterLoader, id=param_settings.RIB_BVD_FABRIC_TYPE_ID):
    pass
