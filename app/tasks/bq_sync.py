"""Periodic BigQuery batch sync for unsynced feedback rows."""

import logging
from app.core.database import AsyncSessionLocal
from app.services.bigquery_export import batch_sync_unsynced

logger = logging.getLogger("bq_sync")


async def sync_pending_feedback():
    """Sync all pending feedback rows to BigQuery."""
    async with AsyncSessionLocal() as db:
        try:
            count = await batch_sync_unsynced(db)
            if count > 0:
                logger.info("Synced %d feedback rows to BigQuery", count)
        except Exception as e:
            logger.error("BQ batch sync failed: %s", e)
