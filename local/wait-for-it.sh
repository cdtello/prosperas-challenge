#!/bin/sh
# Espera a que un host:port esté disponible antes de continuar
# Uso: ./wait-for-it.sh host:port -- comando

HOST=$(echo "$1" | cut -d: -f1)
PORT=$(echo "$1" | cut -d: -f2)
shift

TIMEOUT=60
ELAPSED=0

echo "Esperando $HOST:$PORT..."

while ! nc -z "$HOST" "$PORT" 2>/dev/null; do
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "Timeout esperando $HOST:$PORT"
    exit 1
  fi
  sleep 1
  ELAPSED=$((ELAPSED + 1))
done

echo "$HOST:$PORT disponible — continuando"
exec "$@"
