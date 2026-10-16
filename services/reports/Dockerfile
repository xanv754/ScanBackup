FROM python:3.13.16-slim AS base

ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Caracas

RUN groupadd --gid ${APP_GID} app \
    && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home app \
    && mkdir -p /app /logs /exports \
    && chown app:app /app /logs /exports

WORKDIR /app

ENTRYPOINT ["reports"]


FROM base AS dev

COPY --chown=app:app pyproject.toml README.md ./
COPY --chown=app:app src ./src
RUN pip install -e ".[dev]"

USER app


FROM base AS builder

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip wheel --wheel-dir /wheels .


FROM base AS prod

RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
    pip install --no-index --find-links=/wheels reports

USER app