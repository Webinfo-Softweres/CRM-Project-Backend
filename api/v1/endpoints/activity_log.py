# routes/activity_log.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from db.session import get_db

from models.activity_log import ActivityLog
from models.user import User

from schemas.activity_log import ActivityLogResponseSchema

from core.security import get_current_active_user


router = APIRouter()


@router.get("/", response_model=ActivityLogResponseSchema)
def get_activity_logs(
    skip: int = 0,
    limit: int = 100,

    # Search
    search: str = Query(
        None,
        description="Search by action, endpoint, method, IP address"
    ),

    # Filters
    action: str = None,
    method: str = None,
    user_id: int = None,

    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(ActivityLog)

    # Search
    if search:
        query = query.filter(
            or_(
                ActivityLog.action.ilike(f"%{search}%"),
                ActivityLog.method.ilike(f"%{search}%"),
                ActivityLog.endpoint.ilike(f"%{search}%"),
                ActivityLog.ip_address.ilike(f"%{search}%")
            )
        )

    # Filters
    if action:
        query = query.filter(
            ActivityLog.action.ilike(f"%{action}%")
        )

    if method:
        query = query.filter(
            ActivityLog.method.ilike(f"%{method}%")
        )

    if user_id:
        query = query.filter(
            ActivityLog.user_id == user_id
        )

    total = query.count()

    logs = (
        query
        .order_by(ActivityLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []

    for log in logs:
        items.append({
            "id": log.id,
            "timestamp": log.created_at,

            "user": {
                "id": log.user.id,
                "name": log.user.name,
                "email": log.user.email
            } if log.user else None,

            "action": {
                "method": log.method,
                "name": log.action
            },

            "endpoint": log.endpoint,
            "ip_address": log.ip_address
        })

    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }