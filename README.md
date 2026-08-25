# RAGAB AI Trade Backend

Production-oriented backend foundation for RAGAB AI Trade.

## Scope
- FastAPI API
- PostgreSQL via SQLAlchemy async
- Alembic migrations
- JWT authentication
- User accounts
- Trading accounts
- Paper-trading orders/trades
- AI signal storage
- Risk settings
- Health/readiness endpoints

## Safety
This foundation is PAPER-TRADING ONLY. No broker/exchange execution is implemented.
Never place API keys or passwords in source control.

## Run locally

1. Copy `.env.example` to `.env`.
2. Start PostgreSQL:
   `docker compose -f docker-compose.dev.yml up -d db`
3. Create a virtual environment and install:
   `pip install -r requirements.txt`
4. Run migrations:
   `alembic upgrade head`
5. Start:
   `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

API docs: http://localhost:8000/docs
Health: http://localhost:8000/health
