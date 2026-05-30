
from sqlalchemy.orm import Session

from models.activity_log import ActivityLog


def create_activity_log(
    db: Session,
    user_id: int = None,
    method: str = None,
    action: str = None,
    endpoint: str = None,
    ip_address: str = None
):
    log = ActivityLog(
        user_id=user_id,
        method=method,
        action=action,
        endpoint=endpoint,
        ip_address=ip_address
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log