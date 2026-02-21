FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md /app/
COPY src/ /app/src/
COPY data/processed/ /app/data/processed/

RUN uv sync --frozen --no-dev --group api

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "expert_finder.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
