# FastAPI Listings Backend

FastAPI backend scaffold for managing property listings with async PostgreSQL access and Alembic migrations.

## Features
- Layered architecture (routers → services → repositories → models) for clear separation of concerns.
- Async SQLAlchemy database access with PostgreSQL and Alembic migrations.
- Pydantic models for request/response validation.
- Versioned API routing under `/api/v1`.

## Getting started
1. Ensure Python 3.14.2 is available and install [`uv`](https://github.com/astral-sh/uv):
   ```bash
   pip install uv
   ```
2. Create and activate a virtual environment, then install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv sync
   ```
3. Configure environment variables (see `.env.example`):
   ```bash
   cp .env.example .env
   # update DATABASE_URL if needed
   ```
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API
- `POST /api/v1/listings` – create a listing with pricing, location, and property metadata.

## Migrations
Alembic configuration lives in `alembic/`, with versioned scripts under `alembic/versions/`. Update models in `app/models/` and generate new revisions with:
```bash
alembic revision --autogenerate -m "<message>"
```
