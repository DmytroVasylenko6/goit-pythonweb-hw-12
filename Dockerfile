FROM python:3.12-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y gcc curl libpq-dev python3-dev

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /src

# Копируем зависимости отдельно для кеша
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --only main --no-root

# Копируем остальной код и .env
COPY . .
COPY .env .env

# Добавляем и делаем исполняемым скрипт ожидания
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

EXPOSE 8000

# Используем скрипт ожидания в CMD
CMD ["/bin/sh", "-c", "/wait-for-it.sh db:5432 -- /wait-for-it.sh redis:6379 -- poetry run uvicorn main:app --host 0.0.0.0 --port 8000"]
