FROM python:3.11-slim

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./lib /usr/src/app/lib
RUN pip install --no-cache-dir --upgrade /usr/src/app/lib

COPY . .
