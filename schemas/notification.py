from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum


class NotificationStatus(str, enum.Enum):
    READ = "Read"
    UNREAD = "Unread"


class NotificationBase(BaseModel):
    user_id: int
    message: str
    status: NotificationStatus = NotificationStatus.UNREAD


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    message: Optional[str] = None


class Notification(NotificationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
