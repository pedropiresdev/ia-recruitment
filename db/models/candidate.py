import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.engine import Base


class CandidateModel(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"CAND-{uuid.uuid4().hex[:8].upper()}")
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("selection_processes.id"), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    current_stage: Mapped[str] = mapped_column(String(100), nullable=False, default="inscrito")
    days_in_stage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    screening_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    screening_recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    stage_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
