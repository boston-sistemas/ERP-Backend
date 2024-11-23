import json
import sys
from pathlib import Path
from typing import Type

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent) + "/"
    model_config = SettingsConfigDict(
        env_file=[BASE_DIR + ".env.local", BASE_DIR + ".env"],
        env_ignore_empty=True,
        extra="ignore",
    )
    DATA_DIR: str = BASE_DIR + "initial_data/data/"
    DATABASE_URL: str
    PROMEC_DATABASE_URL: str | None
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_USERNAME: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sys.path.append(self.BASE_DIR)


settings = Settings()


def load_data(file_path: str) -> list[dict]:
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Archivo {file_path} no encontrado.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error al leer el archivo JSON: {str(e)}")
        return []


async def populate(
    db: AsyncSession, model: Type[DeclarativeBase], filename: str
) -> None:
    items = load_data(settings.DATA_DIR + filename)
    created_objects = 0
    for item in items:
        try:
            db.add(model(**item))
            await db.commit()
            created_objects += 1
            logger.info(f"Item creado con éxito: '{item}'.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al crear el item: '{item}', {e}")

    logger.info(f"Numero de items creado: {created_objects}")


if __name__ == "__main__":
    print(settings.model_dump())
