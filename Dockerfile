# syntax=docker/dockerfile:1.7
FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PATH="/root/.local/bin:${PATH}" \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

COPY pyproject.toml ./
RUN uv sync --python /usr/local/bin/python --no-install-project

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app app
COPY alembic alembic
COPY alembic.ini .
COPY README.md .

RUN addgroup --system app \
    && adduser --system --ingroup app --home /app appuser \
    && chown -R appuser:app /app

ENV PATH="/app/.venv/bin:${PATH}" \
    PORT=8000

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
