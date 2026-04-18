from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DiagnosisFeedbackCreate(BaseModel):
    ai_was_correct: bool
    feedback_category: str
    confidence_appropriate: Optional[bool] = None
    severity_mismatch: bool = False
    missed_diagnoses: Optional[list[str]] = None
    incorrect_medications: Optional[list[str]] = None
    feedback_notes: Optional[str] = None


class DiagnosisFeedbackResponse(BaseModel):
    id: int
    diagnosis_id: int
    reviewer_id: int
    ai_was_correct: bool
    feedback_category: str
    confidence_appropriate: Optional[bool] = None
    severity_mismatch: bool
    missed_diagnoses: Optional[list] = None
    incorrect_medications: Optional[list] = None
    feedback_notes: Optional[str] = None
    ai_diagnosis_snapshot: Optional[str] = None
    ai_confidence_snapshot: Optional[float] = None
    ai_severity_snapshot: Optional[str] = None
    ai_model_version_snapshot: Optional[str] = None
    final_diagnosis_snapshot: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
