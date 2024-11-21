import asyncio

from create_admin_user import create_admin_user
from populate_mecsa_colors import populate_mecsa_colors
from populate_parameter_categories import populate_parameter_categories
from populate_parameters import populate_parameters


async def main():
    await create_admin_user()
    await populate_mecsa_colors()
    await populate_parameter_categories()
    await populate_parameters()


if __name__ == "__main__":
    asyncio.run(main())
