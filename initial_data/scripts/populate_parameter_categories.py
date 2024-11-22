import asyncio

from config import populate

from src.core.database import get_db
from src.security.models import ParameterCategory


async def populate_parameter_categories():
    filename = "parameter_categories.json"
    async for db in get_db():
        await populate(db=db, model=ParameterCategory, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_parameter_categories())
