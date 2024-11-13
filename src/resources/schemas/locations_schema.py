from src.core.schemas import CustomBaseModel


class CountrySchema(CustomBaseModel):
    id: str
    name: str


class CountryListSchema(CustomBaseModel):
    countries: list[CountrySchema]
