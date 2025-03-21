import asyncio

from config import populate

from src.core.database import get_db
from src.security.models import ModuloSistema


async def populate_system_modules() -> None:
    filename = "system_modules.json"
    async for db in get_db():
        await populate(db=db, model=ModuloSistema, filename=filename)


if __name__ == "__main__":
    asyncio.run(populate_system_modules())
