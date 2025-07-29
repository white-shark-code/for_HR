#!/bin/sh
set -e

cd /opt/app
. .venv/bin/activate

# Применяем миграции при запуске контейнера
alembic upgrade head

# Запускаем основной процесс
exec "$@"
