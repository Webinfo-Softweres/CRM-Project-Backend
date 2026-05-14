from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class NotificationStatus(str, enum.Enum):
    READ = "Read"
    UNREAD = "Unread"


class Notification(BaseModel):
    __tablename__ = "notifications"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)
    
    user = relationship("User")
