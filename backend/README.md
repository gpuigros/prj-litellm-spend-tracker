# LLM Spend API - Backend

Internal API for tracking LLM expenditure by developer.

## Overview

This FastAPI service aggregates spend data from LiteLLM and provides user-scoped endpoints for viewing expenditure by model, project, and time period.

## Features

- **User-scoped access**: Each user can only see their own spend data
- **Multiple time periods**: Today, week, or month views
- **Model breakdown**: See which LLM models you're using, including token consumption (prompt/completion split)
- **Project attribution**: Track spend by project/repository, including token consumption
- **Budget tracking**: Monitor usage against budget limits
- **Docker-ready**: Fully containerized for easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Build

```bash
export IMAGE=lite-llm-spend-tracker-v1.3
docker buildx build -t $IMAGE . 
docker tag $IMAGE 206360149510.dkr.ecr.eu-west-1.amazonaws.com/automation:$IMAGE \
&& docker push 206360149510.dkr.ecr.eu-west-1.amazonaws.com/automation:$IMAGE
```

### Running with Docker

```bash
# Start the API and database
docker-compose up -d

# View logs
docker-compose logs -f spend-api

# Stop services
docker-compose down
```

The API will be available at:

- API: <http://localhost:8000>
- Documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env

# Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

All endpoints require authentication via Bearer token (LiteLLM virtual API key).

### Spend Endpoints

- `GET /me/spend/summary?period=month` - Get spend summary
- `GET /me/spend/by-model?period=month` - Get spend by model
- `GET /me/spend/by-project?period=month` - Get spend by project
- `GET /me/spend/daily?period=month` - Get daily spend trend

### Budget Endpoint

- `GET /me/budget` - Get budget information

The budget cap is the API key's `max_budget` column on `LiteLLM_VerificationToken` — the same hard cap LiteLLM enforces. The `budget_limits` JSONB rolling window is intentionally **not** used: the budget panel always shows progress against the key's hard cap, not against an arbitrary window. If the key has no `max_budget`, the service falls back to `DEFAULT_MONTHLY_BUDGET`.

### Management Endpoints

Management endpoints are authenticated with the LiteLLM master key (`LITELLM_MASTER_KEY`), not a regular virtual API key. A regular key is rejected with `403 Forbidden`.

- `GET /management/spend?start_date=...&end_date=...` - Get spend for **all** API keys broken down by day and by model. Each entry is one `(api_key, day, model)` tuple. `start_date` and `end_date` are optional and default to the current month.

#### Performance

The management aggregation scans a month of `LiteLLM_SpendLogs` (one row per LLM call). To keep it fast on large tables:

- Model normalization (stripping the provider prefix) is pushed into the SQL `GROUP BY`, so Postgres merges equivalent models before returning rows.
- The query is unordered (the response is an aggregate list with no required ordering).
- A per-connection `statement_timeout` (30s) makes runaway queries fail fast instead of hanging.

> **Database schema ownership:** LiteLLM owns and creates the `LiteLLM_SpendLogs` and `LiteLLM_VerificationToken` tables (and all base indexes) through its own migrations. This service only **reads** from them — it never creates or alters tables. The `init.sql` file in this repo exists solely to seed a **local/test** database for development and the test suite; it is **not** run against the real LiteLLM database.
>
> The only schema-level change this service requires on the real LiteLLM database is a single optional performance index. Apply it once with `sql/management_spend_index.sql`:
>
> ```bash
> psql "$DATABASE_URL" -f sql/management_spend_index.sql
> ```
>
> It uses `CREATE INDEX CONCURRENTLY IF NOT EXISTS`, so it is safe to re-run and does not block LiteLLM writes.

### Periods

- `today` - Current day
- `week` - Current week (Monday to now)
- `month` - Current month (1st to now)

## Configuration

Environment variables (see `.env.example`):

- `DATABASE_URL` - PostgreSQL connection string
- `DB_HOST` / `DB_USER` / `DB_PASSWORD` - Discrete DB connection parts; when `DB_HOST` is set they take precedence over `DATABASE_URL`
- `LITELLM_MASTER_KEY` - LiteLLM master key used to authenticate management endpoints
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)
- `CORS_ORIGINS` - Allowed CORS origins (JSON array)
- `DEFAULT_MONTHLY_BUDGET` - Default budget limit
- `DEFAULT_CURRENCY` - Currency code (EUR, USD, etc.)
- `BUDGET_WARNING_THRESHOLD` - Warning threshold percentage
- `BUDGET_EXCEEDED_THRESHOLD` - Exceeded threshold percentage

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_api/test_spend.py
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and dependencies
│   ├── auth/             # Authentication logic
│   ├── database/         # Database connection
│   ├── models/           # SQLAlchemy and Pydantic models
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI application
├── tests/                # Test suite
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Container image
└── requirements.txt      # Python dependencies
```

## License

PolyForm Noncommercial License 1.0.0 - see [LICENSE](../LICENSE) file for details.

This software is free for noncommercial use, including forking, studying, modifying, and contributing via pull requests. Commercial use requires a separate license from the copyright holder.
