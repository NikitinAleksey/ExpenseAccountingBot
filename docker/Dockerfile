FROM python:3.11-slim

WORKDIR /bot

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /bot/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /bot/

ENV PYTHONPATH=/bot

ENTRYPOINT ["sh", "-c", "alembic -c /bot/app/db/alembic.ini upgrade head && python app/main.py"]