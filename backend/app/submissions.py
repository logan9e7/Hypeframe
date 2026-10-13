"""Community video link submissions: untrusted links remain unpublished pending moderation."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class VideoSubmission(Base):
    __tablename__ = 'video_submissions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    moment_id: Mapped[str] = mapped_column(ForeignKey('moments.id'))
    video_id: Mapped[str] = mapped_column(String(11))
    status: Mapped[str] = mapped_column(String(20), default='pending_review', index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
