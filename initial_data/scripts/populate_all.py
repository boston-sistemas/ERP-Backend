import asyncio

from create_admin_user import create_admin_user
from populate_fibers import populate_fibers
from populate_mecsa_colors import populate_mecsa_colors
from populate_parameter_categories import populate_parameter_categories
from populate_parameters import populate_parameters
from populate_yarn import populate_yarns

from src.core.database import engine_async, promec_async_engine


async def main():
    await create_admin_user()
    await populate_mecsa_colors()
    await populate_parameter_categories()
    await populate_parameters()
    await populate_fibers()
    await populate_yarns()

    await promec_async_engine.dispose()
    await engine_async.dispose()


if __name__ == "__main__":
    asyncio.run(main())
