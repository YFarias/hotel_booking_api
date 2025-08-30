# backend/Dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# deps do sistema (gcc só se precisar compilar libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl netcat-traditional \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements primeiro (melhor cache)
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# copia projeto
COPY . /app/

# porta do Django dev server
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
