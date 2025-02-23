DB_CONTAINER_NAME = mecsa-db
MAILHOG_CONTAINER_NAME = mailhog

run: start_server

stop: stop_db stop_mailhog

setup: start_dependencies install_requirements install_precommit display_odbc_message install_unixodbc

venv:
	source ./venv/bin/activate

install_precommit:
	pip install pre-commit
	pre-commit install

init-db:
	python3 scripts/cli.py init-db

init-promec-db:
	# source ./venv/bin/activate
	python3 scripts/cli.py init-promec-db

populate-all:
	# source ./venv/bin/activate
	python3 initial_data/scripts/populate_all.py

start_server: start_dependencies
	@echo "\nIniciando servidor FastAPI en el puerto 8000..."
	fastapi dev src/main.py --port 8000

start_dependencies: create_volume start_db start_mailhog

create_volume:
	@echo "\nVerificando volumen 'mecsa-data'..."
	docker volume inspect mecsa-data >/dev/null 2>&1 || docker volume create mecsa-data

start_db:
	@echo "\nVerificando contenedor '$(DB_CONTAINER_NAME)'..."
	docker ps -a --format '{{.Names}}' | grep -Fx $(DB_CONTAINER_NAME) >/dev/null 2>&1 || \
	docker run -d --rm \
		--name $(DB_CONTAINER_NAME) \
		-p 5432:5432 \
		-v mecsa-data:/var/lib/postgresql/data \
		-e TZ=America/Lima \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-e POSTGRES_DB=MECSA \
		postgres

start_mailhog:
	@echo "\nVerificando contenedor '$(MAILHOG_CONTAINER_NAME)'..."
	docker ps -a --format '{{.Names}}' | grep -Fx $(MAILHOG_CONTAINER_NAME) >/dev/null 2>&1 || \
	docker run -d --rm \
		--name $(MAILHOG_CONTAINER_NAME) \
		-p 1025:1025 \
		-p 8025:8025 \
		mailhog/mailhog

install_requirements:
	@echo "Instalando dependencias de Python..."
	pip install -r requirements.txt
	pip install ./lib

display_odbc_message:
	@echo "\n\t\t=================================================="
	@echo "\t\t ¡No olvides instalar el driver ODBC de Progress! "
	@echo "\t\t=================================================="

install_unixodbc:
	@echo "Instalando unixODBC..."
	- sudo apt-get install unixodbc

stop_db:
	@echo "\nDeteniendo contenedor '$(DB_CONTAINER_NAME)' si está en ejecución..."
	- docker ps --format '{{.Names}}' | grep -Fx $(DB_CONTAINER_NAME) >/dev/null 2>&1 && \
	docker stop $(DB_CONTAINER_NAME)

stop_mailhog:
	@echo "\nDeteniendo contenedor '$(MAILHOG_CONTAINER_NAME)' si está en ejecución..."
	- docker ps --format '{{.Names}}' | grep -Fx $(MAILHOG_CONTAINER_NAME) >/dev/null 2>&1 && \
	docker stop $(MAILHOG_CONTAINER_NAME)

uvicorn start:
	uvicorn --app-dir src/ main:app --host 0.0.0.0 --port 8000 --reload
