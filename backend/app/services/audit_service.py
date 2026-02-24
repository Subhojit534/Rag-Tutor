"""
Audit Service - Logging admin actions
"""
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.system import AuditLog
import json


def log_action(
    db: Session,
    user_id: int,
    action: str,
    entity: str,
    entity_id: Optional[int] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None
):
    """
    Log an admin action to the audit_logs table.
    
    Actions:
    - subject_created, subject_updated, subject_deactivated
    - semester_progression
    - teacher_allocated, teacher_deallocated
    - user_activated, user_deactivated
    - quiz_created, assignment_created
    - setting_updated
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address
    )
    db.add(audit_log)
    # Note: Caller should handle commit
