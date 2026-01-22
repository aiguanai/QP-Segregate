from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog
from typing import Optional, Dict, Any

def log_activity(
    db: Session,
    user_id: int,
    activity_type: str,
    description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Utility function to log activities"""
    activity_log = ActivityLog(
        user_id=user_id,
        activity_type=activity_type,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        description=description,
        activity_metadata=metadata  # Using activity_metadata instead of metadata
    )
    db.add(activity_log)
    db.commit()
    return activity_log

