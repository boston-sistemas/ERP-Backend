import gettext
from functools import lru_cache

import pycountry
from fastapi import APIRouter
from pydantic_extra_types.country import _countries

from src.resources.schemas import CountryListSchema, CountrySchema

spanish = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["es"])
spanish.install()
_ = spanish.gettext

router = APIRouter()


@lru_cache
def _read_countries() -> CountryListSchema:
    return CountryListSchema(
        countries=[
            CountrySchema(id=country.alpha3, name=_(country.short_name))
            for country in _countries()
        ]
    )


@router.get("/countries/", response_model=CountryListSchema)
async def read_countries():
    return _read_countries()
