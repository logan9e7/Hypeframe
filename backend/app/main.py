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
