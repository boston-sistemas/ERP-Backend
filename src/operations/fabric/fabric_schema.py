from src.core.schemas import CustomBaseModel


class BaseFabricOptions(CustomBaseModel):
    include_fabric_type: bool = False
    include_recipe: bool = False
    include_yarn_instance: bool = False

    @staticmethod
    def all() -> "BaseFabricOptions":
        return BaseFabricOptions(
            include_fabric_type=True,
            include_recipe=True,
            include_yarn_instance=True,
        )
