# FastAPI Listings Backend

FastAPI backend scaffold for managing property listings with async PostgreSQL access and Alembic migrations.

## Features
- Layered architecture (routers → services → repositories → models) for clear separation of concerns.
- Async SQLAlchemy database access with PostgreSQL and Alembic migrations.
- Pydantic models for request/response validation.
- Versioned API routing under `/api/v1`.
- JWT-based authentication with role-aware authorization guards.
- Listing image uploads stored in Google Cloud Storage.

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
   - Set `CORS_ORIGINS` to a comma-separated list of frontend URLs (defaults include `https://property-systems.memcommerce.shop`,
     `http://localhost:3000`, and `http://localhost:5173`). The same value should be provided to deployment manifests to allow
     browsers to call the API.
   - Provide `BUCKET_NAME` and `SA_KEY_PATH` for Google Cloud Storage uploads. The service account file should be mounted in the
     container (see `infra/deployment.yaml` for an example Kubernetes volume mount).
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
- `GET /api/v1/listings/{listing_id}` – fetch a listing by its identifier, including associated images.
- `POST /api/v1/listings/{listing_id}/images` – upload an image file for a listing; stores the image in GCS and returns its URL.
- `POST /api/v1/auth/register` – register a user account.
- `POST /api/v1/auth/login` – obtain an access token.
- `GET /api/v1/auth/me` – retrieve the authenticated user's profile.

## Migrations
Alembic configuration lives in `alembic/`, with versioned scripts under `alembic/versions/`. Update models in `app/models/` and generate new revisions with:
```bash
alembic revision --autogenerate -m "<message>"
```
