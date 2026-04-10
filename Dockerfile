FROM python:3.12-slim

WORKDIR /app

RUN pip install uv --quiet

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .
RUN chmod +x scripts/start-*.sh
