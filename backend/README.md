# Hypeframe Python API

FastAPI + SQLAlchemy. SQLite for local development; PostgreSQL in production.

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

Test: `pytest -q`

Endpoints: `GET /health`, `GET /api/moments`, `GET /api/moments/{id}`, `GET /api/moments/{id}/hype`.

**Security:** Vote and collection tables are defined, but write endpoints are deliberately disabled until authenticated identities and authorization checks are implemented. No fake community-wide voting claims.

Production: configure `DATABASE_URL` with PostgreSQL, set `CORS_ORIGINS` to your deployed frontend, use Alembic migrations, and deploy backend as a web service.
