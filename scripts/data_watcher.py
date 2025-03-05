from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from time import time

from loguru import logger
from sqlalchemy import text
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import AsyncSession


class DataWatcher:
    def __init__(self, promec_engine: Engine) -> None:
        self.promec_engine = promec_engine
        self.file_lock = Lock()

    async def write_table_name(
        self, output_file: str = "filtered_table_names.txt"
    ) -> None:
        async with AsyncSession(bind=self.promec_engine) as session:
            query = text("""
                SELECT "_File-Name" AS table_name
                FROM PUB."_File"
                WHERE "_Owner" = 'PUB'
            """)
            result = await session.execute(query)

            with open(output_file, "w") as file:
                rows = result.fetchall()
                filtered_rows = [row[0] for row in rows if not row[0].startswith("_")]
                for table_name in filtered_rows:
                    file.write(f"{table_name}\n")
                    logger.info(f"Tabla encontrada: {table_name}")
                file.write("_plancta\n")
                logger.info("Tabla encontrada: _plancta")
            logger.info(f"Se han guardado los nombres de las tablas en {output_file}.")

    async def count_rows_for_table(self, table_name: str) -> tuple[str, int]:
        try:
            async with AsyncSession(bind=self.promec_engine) as session:
                query = text(f'SELECT COUNT(*) AS row_count FROM PUB."{table_name}"')
                result = await session.execute(query)
                return table_name, result.scalar()
        except Exception as e:
            logger.error(f"Error al contar las filas de la tabla {table_name}: {e}")
            return table_name, 0

    async def save_row_count_to_file(
        self, table_name: str, row_count: int, output_file: str
    ) -> None:
        with self.file_lock:
            try:
                with open(output_file, "a") as file:
                    file.write(f"{table_name}:{row_count}\n")
                    logger.info(f"Guardado inicial: {table_name} -> {row_count}")
            except Exception as e:
                logger.error(
                    f"Error al escribir en el archivo {output_file} para {table_name}: {e}"
                )

    async def save_initital_row_counts_parallel(
        self, table_names: str, output_file: str, max_workers: int = 5
    ) -> int:
        with open(output_file, "w"):
            pass
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.count_rows_for_table, table_name): table_name
                for table_name in table_names
            }

            for future in as_completed(futures):
                table_name, row_count = future.result()
                if row_count is not None:
                    self.save_row_count_to_file(table_name, row_count, output_file)

    async def get_table_row_counts_parallel(
        self, table_names: str, max_workers: int = 5
    ) -> int:
        start_time = time()
        row_counts = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.count_rows_for_table, table_name): table_name
                for table_name in table_names
            }

            for future in as_completed(futures):
                table_name, row_count = future.result()
                if row_count is not None:
                    row_counts[table_name] = row_count

        elapsed_time = time() - start_time
        logger.info(f"Conteo de filas completado en {elapsed_time:.2f} segundos.")
        return row_counts

    async def detect_altered_tables(self, current_counts, previous_counts_file):
        altered_tables = []

        with open(previous_counts_file, "r") as file:
            previous_counts = {
                line.split(":")[0]: int(line.split(":")[1])
                for line in file
                if ":" in line
            }

        for table_name, current_count in current_counts.items():
            if current_count is None:
                logger.warning(f"No se pudo contar filas para la tabla {table_name}.")
                continue

            previous_count = previous_counts.get(table_name)

            if previous_count is None:
                logger.info(
                    f"Tabla nueva detectada: {table_name} con {current_count} filas."
                )
                altered_tables.append((table_name, "nueva", current_count))
            elif current_count != previous_count:
                logger.info(
                    f"Tabla alterada: {table_name}, previo: {previous_count}, actual: {current_count}."
                )
                altered_tables.append((table_name, previous_count, current_count))

        return altered_tables
