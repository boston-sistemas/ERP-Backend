import asyncio

from config import settings
from loguru import logger
from sqlalchemy import select

from src.core.database import get_db
from src.core.utils import calculate_time
from src.security.models import Usuario
from src.security.services import HashService


async def create_admin_user() -> None:
    async for db in get_db():
        result = await db.execute(
            select(Usuario).where(Usuario.username == settings.ADMIN_USERNAME)
        )
        exists_admin_user = result.scalar_one_or_none()

        if exists_admin_user:
            logger.error("USUARIO ADMINISTRADOR YA EXISTE.")
            return None

        hashed_password = HashService.hash_text(settings.ADMIN_PASSWORD)

        admin_user = Usuario(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=hashed_password,
            display_name="ADMINISTRADOR - MECSA",
            is_active=True,
            reset_password_at=calculate_time(days=30),
        )

        db.add(admin_user)
        await db.commit()
        logger.info("USUARIO ADMINISTRADOR CREADO CON ÉXITO")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
