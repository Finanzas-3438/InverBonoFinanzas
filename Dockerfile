# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app/InverBono

RUN pip install -r ../requirements.txt
RUN python manage.py collectstatic --noinput

