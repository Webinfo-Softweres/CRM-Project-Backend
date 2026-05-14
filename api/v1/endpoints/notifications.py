from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.notification import Notification
from models.user import User
from schemas.notification import Notification as NotificationSchema, NotificationCreate, NotificationUpdate
from core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=NotificationSchema, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == notification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_notification = Notification(
        user_id=notification.user_id,
        message=notification.message,
        status=notification.status
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.get("/", response_model=List[NotificationSchema])
def get_notifications(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).offset(skip).limit(limit).all()
    return notifications


@router.get("/user/{user_id}", response_model=List[NotificationSchema])
def get_notifications_by_user(user_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
    return notifications


@router.get("/user/{user_id}/unread", response_model=List[NotificationSchema])
def get_unread_notifications(user_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.status == "Unread"
    ).all()
    return notifications


@router.get("/{notification_id}", response_model=NotificationSchema)
def get_notification(notification_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.put("/{notification_id}", response_model=NotificationSchema)
def update_notification(notification_id: int, notification: NotificationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_data = notification.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.put("/{notification_id}/mark-read", response_model=NotificationSchema)
def mark_notification_read(notification_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db_notification.status = "Read"
    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(db_notification)
    db.commit()
