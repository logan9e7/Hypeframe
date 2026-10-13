from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Moment(Base):
    __tablename__ = 'moments'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    anime: Mapped[str] = mapped_column(String(150), index=True)
    title: Mapped[str] = mapped_column(String(200))
    episode: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text)
    spoiler: Mapped[bool] = mapped_column(default=True)
    accent: Mapped[str] = mapped_column(String(12), default='#f26443')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Vote(Base):
    __tablename__ = 'votes'
    __table_args__ = (UniqueConstraint('moment_id', 'user_id'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    moment_id: Mapped[str] = mapped_column(ForeignKey('moments.id', ondelete='CASCADE'))
    user_id: Mapped[str] = mapped_column(String(100), index=True)

class Collection(Base):
    __tablename__ = 'collections'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(120))

class CollectionItem(Base):
    __tablename__ = 'collection_items'
    __table_args__ = (UniqueConstraint('collection_id', 'moment_id'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey('collections.id', ondelete='CASCADE'))
    moment_id: Mapped[str] = mapped_column(ForeignKey('moments.id', ondelete='CASCADE'))
