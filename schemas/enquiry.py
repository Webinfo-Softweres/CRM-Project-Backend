from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum


class EnquiryStatus(str, enum.Enum):
    NEW = "New"
    FOLLOW_UP = "Follow-up"
    CLOSED = "Closed"


class EnquiryBase(BaseModel):
    customer_id: int
    source: Optional[str] = None
    service_required: Optional[str] = None
    description: Optional[str] = None
    status: EnquiryStatus = EnquiryStatus.NEW
    assigned_to: Optional[int] = None


class EnquiryCreate(EnquiryBase):
    pass


class EnquiryUpdate(BaseModel):
    customer_id: Optional[int] = None
    source: Optional[str] = None
    service_required: Optional[str] = None
    description: Optional[str] = None
    status: Optional[EnquiryStatus] = None
    assigned_to: Optional[int] = None


class EnquiryAssign(BaseModel):
    assigned_to: int


class EnquiryStatusUpdate(BaseModel):
    status: EnquiryStatus


class Enquiry(EnquiryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
