# Project Template

FastAPI backend, static HTML frontend, no build step. SQLite + Alembic for migrations. uv for package management.

## Setup

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000

## Migrations

```bash
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

## Test

```bash
uv run pytest
```

## Structure

- `app/` — FastAPI backend (routes, models, schemas, db)
- `static/` — HTML, CSS, JS served directly, no templating
- `alembic/` — database migrations
- `docs/` — domain and architecture docs
- `AGENT.md` — agent workflow instructions
