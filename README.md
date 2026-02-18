# Fast Lego (FastAPI + Postgres + Jinja)

## Features
- FastAPI app with API and HTML endpoints
- Postgres via Docker Compose
- SQLModel data models (`CatalogItem`, `SearchLog`)
- Startup seed for a simple searchable catalog
- Shared database connectivity file: `app/db/Connection.py`
- Environment-driven configuration object loaded from `.env` files
- Unit tests colocated with source modules

## Endpoints
- `GET /health` - returns service and database status
- `GET /` - welcome page
- `GET /about` - about page
- `GET /search` - search form page
- `POST /search` - database-backed search over seeded catalog items

## API response contract
Successful API responses follow:
```json
{
  "data": {},
  "continuationToken": "optional",
  "next": "optional",
  "message": "optional"
}
```

Error API responses follow:
```json
{
  "message": "string",
  "action": "retry | modify_request | not_auth | internal_error",
  "x-request-id": "string"
}
```

Every response includes an `x-request-id` header (HTML and API).

## Run in development (containerized)
```bash
docker compose up --build
```

Then open:
- [http://localhost:8000/](http://localhost:8000/)
- [http://localhost:8000/health](http://localhost:8000/health)

## Run tests
```bash
pytest
```

Or run tests in the API container:
```bash
docker compose run --rm api pytest
```

This works because `docker-compose.yml` builds the `development` Docker stage, which includes test dependencies.

## Makefile shortcuts
```bash
make build
make start
make stop
```

Database helpers:
```bash
make db-setup   # create tables
make db-seed    # seed catalog
make db-init    # create tables + seed
```

Note: app startup already runs setup + seed automatically and seeding is idempotent.

## Production image
Build a lean production image (without pytest/httpx):
```bash
docker build --target production -t fast-lego:prod .
```
