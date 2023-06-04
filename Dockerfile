FROM python:3.10.8-alpine

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH=/app
ENV MUSL_LOCPATH="/usr/share/i18n/locales/musl"

RUN apk add --no-cache \
    curl `# для установки poetry` \
    gcc `# для установки poetry` \
    libffi-dev `# для установки poetry` \
    git `# для установки зависимостей из git` \
    build-base  `# для сборки пакетов` \
    postgresql-dev `# для psycopg2` \
    musl-locales musl-locales-lang `# для работы русской локали в python`

RUN pip3 install --upgrade pip
RUN pip3 install poetry
RUN mkdir /app
COPY pyproject.toml poetry.lock /app/
WORKDIR /app/
RUN poetry install --no-interaction --no-ansi --no-root
COPY / /app/
RUN chmod +x entrypoint.sh
