from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Integer, Boolean, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class DiagnosisFeedback(Base):
    __tablename__ = "diagnosis_feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    diagnosis_id: Mapped[int] = mapped_column(Integer, ForeignKey("diagnoses.id"), nullable=False, index=True)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Core feedback
    ai_was_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    confidence_appropriate: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # What went wrong (structured)
    severity_mismatch: Mapped[bool] = mapped_column(Boolean, default=False)
    missed_diagnoses: Mapped[list | None] = mapped_column(JSON, nullable=True)
    incorrect_medications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    feedback_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Snapshot of AI output at time of feedback (denormalized for BigQuery export)
    ai_diagnosis_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_confidence_snapshot: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_severity_snapshot: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ai_model_version_snapshot: Mapped[str | None] = mapped_column(String(100), nullable=True)
    final_diagnosis_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    synced_to_bq: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
