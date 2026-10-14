import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Moment, Vote, Collection, CollectionItem
from .submissions import VideoSubmission
from .video_discovery import parse_youtube_id
from fastapi import Request
from datetime import datetime, timedelta, timezone
from threading import Lock
import json
import logging
from pathlib import Path
from functools import lru_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # MVP only; replace with Alembic migrations before production
    from .seed import seed
    seed()  # Render free filesystem is ephemeral; seed runtime DB, not only build instance
    yield

app = FastAPI(title='Hypeframe API', version='0.1.0', lifespan=lifespan)
origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://hypeframe-web.netlify.app').split(',')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['*'])

def db_session():
    with SessionLocal() as db:
        yield db

DB = Annotated[Session, Depends(db_session)]

class MomentOut(BaseModel):
    id: str
    anime: str
    title: str
    episode: str
    category: str
    description: str
    spoiler: bool
    accent: str
    model_config = {'from_attributes': True}

class CollectionIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)

@app.get('/health')
def health():
    return {'status': 'ok', 'video_discovery_configured': bool(os.getenv('YOUTUBE_API_KEY')), 'database': 'sqlite' if engine.dialect.name == 'sqlite' else 'postgresql'}

@app.get('/api/moments', response_model=list[MomentOut])
def list_moments(db: DB, q: str = Query('', max_length=120), category: str | None = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    stmt = select(Moment)
    if q:
        stmt = stmt.where(Moment.title.ilike(f'%{q}%') | Moment.anime.ilike(f'%{q}%'))
    if category:
        stmt = stmt.where(Moment.category == category)
    return db.scalars(stmt.order_by(Moment.created_at, Moment.id).limit(limit).offset(offset)).all()

@app.get('/api/moments/{moment_id}', response_model=MomentOut)
def get_moment(moment_id: str, db: DB):
    item = db.get(Moment, moment_id)
    if not item:
        raise HTTPException(404, 'Moment not found')
    return item

@app.get('/api/moments/{moment_id}/hype')
def hype_count(moment_id: str, db: DB):
    if not db.get(Moment, moment_id):
        raise HTTPException(404, 'Moment not found')
    return {'moment_id': moment_id, 'count': db.scalar(select(func.count()).select_from(Vote).where(Vote.moment_id == moment_id))}

# Voting and collection writes are intentionally not exposed until verified user authentication exists.
# Never accept an arbitrary client-supplied user_id as proof of identity.


class VideoSubmissionIn(BaseModel):
    moment_id: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=15, max_length=500)

# Best-effort per-process abuse protection; use shared Redis / edge rate limits before scaling.
_submit_times: dict[str, datetime] = {}
_submit_lock = Lock()

# Legacy anonymous write endpoint disabled: submissions require Supabase Auth + RLS.
@app.post('/api/video-submissions', status_code=410)
def legacy_video_submission():
    raise HTTPException(410, 'Use authenticated Supabase video submissions at /submit')


@app.get('/api/anime/search')
def search_anime(request: Request, q: str = Query(..., min_length=2, max_length=100), provider: str = Query('all', pattern='^(all|jikan|anilist|kitsu)$'), limit: int = Query(5, ge=1, le=10)):
    """Read-only catalog search, cached for a day; never returns hosted anime video."""
    from .providers import search_metadata
    # Limit unique requests per IP to avoid turning the API into an unbounded free-provider proxy.
    client_ip = request.client.host if request.client else 'unknown'
    now = datetime.now(timezone.utc)
    key = 'anime:' + client_ip
    with _submit_lock:
        previous = _submit_times.get(key)
        if previous and now - previous < timedelta(seconds=10):
            raise HTTPException(429, 'Please wait before searching again')
        _submit_times[key] = now
    return search_metadata(q, provider, limit)


@app.get('/api/videos/discover')
def discover_video_previews(request: Request, anime: str = Query(..., min_length=2, max_length=100), moment: str = Query(..., min_length=2, max_length=150), limit: int = Query(3, ge=1, le=5)):
    """Search public embeddable YouTube videos. Search previews are NOT moderator-approved or licensed by Hypeframe."""
    from .video_discovery import discover_candidates
    from urllib.error import HTTPError, URLError
    client_ip = request.client.host if request.client else 'unknown'
    key = 'video:' + client_ip
    now = datetime.now(timezone.utc)
    with _submit_lock:
        previous = _submit_times.get(key)
        if previous and now - previous < timedelta(seconds=30):
            raise HTTPException(429, 'Please wait 30 seconds before another video search')
        _submit_times[key] = now
    if not os.getenv('YOUTUBE_API_KEY'):
        raise HTTPException(503, 'YouTube API key missing from the running Render service. Set YOUTUBE_API_KEY in hypeframe-api Environment and redeploy.')
    try:
        return {'results': discover_candidates(anime, moment, limit), 'reviewed': False}
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(502, 'YouTube video discovery is temporarily unavailable') from exc


# Quota-safe discovery: one pass per 24 hours, persisted on the service filesystem.
# For multiple instances or ephemeral restarts, replace with a shared durable cache.
_featured_cache = {'at': None, 'results': []}
_featured_lock = Lock()
_featured_path = Path(os.getenv('FEATURED_CACHE_PATH', '/tmp/hypeframe-featured-cache.json'))
_featured_budget = 12

def _load_featured():
    try:
        data = json.loads(_featured_path.read_text())
        refreshed = datetime.fromisoformat(data['at'])
        if refreshed.tzinfo and datetime.now(timezone.utc) - refreshed < timedelta(hours=24):
            return data['results']
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None

@app.get('/api/videos/featured')
def featured_video_previews(limit: int = Query(12, ge=1, le=12)):
    from .video_discovery import discover_candidates
    from .seed import SEED
    from urllib.error import HTTPError, URLError
    if not os.getenv('YOUTUBE_API_KEY'):
        raise HTTPException(503, 'YouTube API key not configured')
    now = datetime.now(timezone.utc)
    with _featured_lock:
        previous = _featured_cache['at']
        if previous and now - previous < timedelta(hours=24):
            return {'results': _featured_cache['results'][:limit], 'reviewed': False, 'curator': 'Hypeframe Curator'}
        stored = _load_featured()
        if stored is not None:
            _featured_cache.update(at=now,results=stored)
            return {'results': stored[:limit], 'reviewed': False, 'curator': 'Hypeframe Curator'}
        results = []
        # Search API consumes 100 quota units per moment. Never exceed 12 searches per refresh.
        for entry in SEED[:_featured_budget]:
            moment_id, anime, title = entry[:3]
            try:
                candidates = discover_candidates(anime, title, 3)
                if candidates:
                    results.append({'moment_id': moment_id, **candidates[0]})
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                logging.warning('YouTube discovery failed for moment %s: %s', moment_id, type(exc).__name__)
                continue
        _featured_cache.update(at=now,results=results)
        try:
            _featured_path.parent.mkdir(parents=True,exist_ok=True)
            temp = _featured_path.with_suffix('.tmp')
            temp.write_text(json.dumps({'at':now.isoformat(),'results':results}))
            temp.replace(_featured_path)
        except OSError:
            logging.warning('Featured video cache could not be persisted')
        return {'results': results[:limit], 'reviewed': False, 'curator': 'Hypeframe Curator'}
