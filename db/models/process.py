import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.engine import Base


class SelectionProcessModel(Base):
    __tablename__ = "selection_processes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"PROC-{uuid.uuid4().hex[:8].upper()}")
    opening_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("job_openings.id"), nullable=True, index=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    recruiter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recruiter_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="em_aberto")
    sla_status: Mapped[str] = mapped_column(String(50), nullable=False, default="no_prazo")
    sla_deadline_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspension_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_candidates_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    timeline: Mapped[list["ProcessTimelineModel"]] = relationship(
        back_populates="process", cascade="all, delete-orphan", order_by="ProcessTimelineModel.event_date"
    )


class ProcessTimelineModel(Base):
    __tablename__ = "process_timeline"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process_id: Mapped[str] = mapped_column(String(36), ForeignKey("selection_processes.id"), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(255), nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    process: Mapped["SelectionProcessModel"] = relationship(back_populates="timeline")
