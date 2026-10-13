# Deployment checklist

## 1. Verify CI

Check the GitHub Actions tab for both `Frontend checks` and `Python API checks`. A committed workflow is not proof of a passing run.

## 2. Python API on Render

Create a web service from this repo using `render.yaml` as a blueprint, or manually set root directory `backend`, build `pip install -r requirements.txt && python -m app.seed`, and start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set `CORS_ORIGINS` to the real frontend origin. SQLite on free Render is temporary; use a persistent PostgreSQL `DATABASE_URL` for production.

## 3. Next.js frontend

Import this GitHub repo into Vercel or Netlify. Build command: `npm run build`. Set `NEXT_PUBLIC_API_URL` to the deployed API base URL, then redeploy. Without this variable the bundled 12-moment preview catalog remains available.

## 4. Verify

- Backend `/health` returns `{\"status\":\"ok\"}`
- Backend `/api/moments` returns curated records after seeding
- Frontend loads, search works, spoilers remain hidden by default
- API CORS permits only expected origins

## Not yet production ready

Authenticated community voting, user-created collections, durable production migrations, and moderation are pending. Local browser votes are not shared with other users.
