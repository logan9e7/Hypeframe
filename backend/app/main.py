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

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # MVP only; replace with Alembic migrations before production
    yield

app = FastAPI(title='Hypeframe API', version='0.1.0', lifespan=lifespan)
origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
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
    return {'status': 'ok'}

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

@app.post('/api/video-submissions', status_code=202)
def submit_video(payload: VideoSubmissionIn, request: Request, db: DB):
    video_id = parse_youtube_id(payload.url)
    if not video_id:
        raise HTTPException(422, 'Only valid YouTube video links are accepted')
    if not db.get(Moment, payload.moment_id):
        raise HTTPException(404, 'Moment not found')
    client_ip = request.client.host if request.client else 'unknown'
    now = datetime.now(timezone.utc)
    with _submit_lock:
        previous = _submit_times.get(client_ip)
        if previous and now - previous < timedelta(minutes=2):
            raise HTTPException(429, 'Please wait before submitting another link')
        _submit_times[client_ip] = now
    existing = db.scalar(select(VideoSubmission).where(VideoSubmission.moment_id == payload.moment_id, VideoSubmission.video_id == video_id))
    if existing:
        return {'status': 'pending_review', 'message': 'Link received for review'}
    db.add(VideoSubmission(moment_id=payload.moment_id, video_id=video_id))
    db.commit()
    return {'status': 'pending_review', 'message': 'Link received for review'}
