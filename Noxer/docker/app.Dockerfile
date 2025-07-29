FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Установка системных зависимостей
RUN apk update && \
    apk add --no-cache \
        build-base \
        postgresql-dev

WORKDIR /opt/app

# Копирование только необходимых для установки зависимостей файлов
COPY pyproject.toml ./

# Установка зависимостей
RUN uv venv && source .venv/bin/activate && uv sync --extra postgresql

# Копирование всего проекта
COPY . .

# Очистка кэша и временных файлов
RUN find . -name '*.pyc' -delete && \
    find . -name '__pycache__' -delete && \
    rm -rf /tmp/*

# Порт для приложения
EXPOSE 8080

COPY ./.env ./.env

COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


# Стартовая команда (переопределяется в compose)
# CMD [".venv/bin/alembic", "upgrade", "head", "&&", ".venv/bin/gunicorn", "-c", "gunicorn_cfg.py", "flask_app:app"]