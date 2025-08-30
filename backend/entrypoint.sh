#!/bin/sh
set -e

# Defaults  
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
WAIT_REDIS="${WAIT_REDIS:-1}"         
MIGRATE_ON_START="${MIGRATE_ON_START:-1}"  
COLLECTSTATIC="${COLLECTSTATIC:-0}"    

echo "[entrypoint] DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-project.settings}"
echo "[entrypoint] REDIS_HOST=$REDIS_HOST REDIS_PORT=$REDIS_PORT"

# Wait for Redis (uses /bin/sh; no {1..N})
if [ "$WAIT_REDIS" = "1" ]; then
  echo "[entrypoint] Aguardando Redis em $REDIS_HOST:$REDIS_PORT ..."
  i=1
  while [ $i -le 30 ]; do
    if nc -z "$REDIS_HOST" "$REDIS_PORT" >/dev/null 2>&1; then
      echo "[entrypoint] Redis disponível."
      break
    fi
    echo "[entrypoint] Tentativa $i/30: Redis ainda não respondeu..."
    i=$((i+1))
    sleep 2
  done
fi

# Migrations (optional)
if [ "$MIGRATE_ON_START" = "1" ]; then
  echo "[entrypoint] Executando migrações..."
  python manage.py migrate --noinput
fi

# Coleta de estáticos (opcional; útil em prod)
if [ "$COLLECTSTATIC" = "1" ]; then
  echo "[entrypoint] Coletando arquivos estáticos..."
  python manage.py collectstatic --noinput
fi

echo "[entrypoint] Iniciando comando: $*"
exec "$@"
