
#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

if [ ! -f ".venv/bin/python" ]; then
    echo "No se encontro el entorno virtual .venv"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "No se encontro el archivo .env"
    exit 1
fi

echo "Iniciando Smart Glasses API..."

exec .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8000
