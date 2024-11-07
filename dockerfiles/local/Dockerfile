FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends unixodbc && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./lib /usr/src/app/lib
RUN pip install --no-cache-dir --upgrade /usr/src/app/lib

COPY . .

CMD ["fastapi", "dev", "src/main.py"]
