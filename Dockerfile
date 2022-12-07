FROM python:3.9.0-slim

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Moscow

WORKDIR /app

RUN pip install -q --no-cache-dir croniter aiogram

COPY *.py ./

ENTRYPOINT ["python3", "main.py"]
