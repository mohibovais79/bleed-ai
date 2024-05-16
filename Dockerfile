FROM python:3.11.5-slim

WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt
