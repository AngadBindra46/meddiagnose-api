"""
BigQuery export service for diagnosis feedback.

Uses streaming inserts for low-latency event-driven export.
Falls back to batch sync for any rows where synced_to_bq=False.
"""

import asyncio
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger("bigquery_export")

_bq_client = None


def _get_client():
    """Lazy-init BigQuery client. Returns None if not configured."""
    global _bq_client
    if _bq_client is not None:
        return _bq_client
    settings = get_settings()
    if not settings.GCP_PROJECT_ID or not settings.BQ_DATASET_ID:
        return None
    try:
        from google.cloud import bigquery
        _bq_client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        logger.info("BigQuery client initialized for project %s", settings.GCP_PROJECT_ID)
        return _bq_client
    except Exception as e:
        logger.warning("BigQuery client init failed: %s", e)
        return None


def _feedback_to_bq_row(fb) -> dict[str, Any]:
    """Convert a DiagnosisFeedback ORM instance or dict to a BigQuery row."""
    if isinstance(fb, dict):
        return fb
    return {
        "id": fb.id,
        "diagnosis_id": fb.diagnosis_id,
        "reviewer_id": fb.reviewer_id,
        "ai_was_correct": fb.ai_was_correct,
        "feedback_category": fb.feedback_category,
        "confidence_appropriate": fb.confidence_appropriate,
        "severity_mismatch": fb.severity_mismatch,
        "missed_diagnoses": fb.missed_diagnoses,
        "incorrect_medications": fb.incorrect_medications,
        "feedback_notes": fb.feedback_notes,
        "ai_diagnosis_snapshot": fb.ai_diagnosis_snapshot,
        "ai_confidence_snapshot": fb.ai_confidence_snapshot,
        "ai_severity_snapshot": fb.ai_severity_snapshot,
        "ai_model_version_snapshot": fb.ai_model_version_snapshot,
        "final_diagnosis_snapshot": fb.final_diagnosis_snapshot,
        "created_at": fb.created_at.isoformat() if fb.created_at else None,
    }


async def stream_feedback_to_bq(feedback_row: dict[str, Any]) -> bool:
    """
    Streaming insert a single feedback row to BigQuery.
    Returns True on success, False on failure.
    """
    client = _get_client()
    if not client:
        return False
    settings = get_settings()
    table_id = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET_ID}.{settings.BQ_FEEDBACK_TABLE}"
    try:
        errors = await asyncio.to_thread(
            client.insert_rows_json, table_id, [feedback_row]
        )
        if errors:
            logger.error("BigQuery streaming insert errors: %s", errors)
            return False
        return True
    except Exception as e:
        logger.error("BigQuery streaming insert failed: %s", e)
        return False


async def batch_sync_unsynced(db_session) -> int:
    """
    Sync all feedback rows where synced_to_bq=False.
    Called periodically as a fallback for failed streaming inserts.
    Returns count of rows synced.
    """
    client = _get_client()
    if not client:
        return 0
    settings = get_settings()
    table_id = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET_ID}.{settings.BQ_FEEDBACK_TABLE}"

    from sqlalchemy import select, update
    from app.models.diagnosis_feedback import DiagnosisFeedback

    result = await db_session.execute(
        select(DiagnosisFeedback).where(DiagnosisFeedback.synced_to_bq == False).limit(500)
    )
    rows = result.scalars().all()
    if not rows:
        return 0

    bq_rows = [_feedback_to_bq_row(r) for r in rows]
    try:
        errors = await asyncio.to_thread(client.insert_rows_json, table_id, bq_rows)
        if errors:
            logger.error("BigQuery batch sync errors: %s", errors)
            return 0
    except Exception as e:
        logger.error("BigQuery batch sync failed: %s", e)
        return 0

    ids = [r.id for r in rows]
    await db_session.execute(
        update(DiagnosisFeedback)
        .where(DiagnosisFeedback.id.in_(ids))
        .values(synced_to_bq=True)
    )
    await db_session.commit()
    return len(ids)
