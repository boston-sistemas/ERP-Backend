from src.core.schemas import CustomBaseModel


class UnitSchema(CustomBaseModel):
    code: str
    description: str
    derived_units: list["DerivedUnitSchema"]

    class Config:
        from_attributes = True


class UnitListSchema(CustomBaseModel):
    units: list[UnitSchema]


class DerivedUnitSchema(CustomBaseModel):
    code: str
    base_code: str
    description: str
    factor: float
    sunat_code: str

    class Config:
        from_attributes = True


class DerivedUnitListSchema(CustomBaseModel):
    derived_units: list[DerivedUnitSchema]
