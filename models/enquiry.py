from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class EnquiryStatus(str, enum.Enum):
    NEW = "New"
    FOLLOW_UP = "Follow-up"
    CLOSED = "Closed"


class Enquiry(BaseModel):
    __tablename__ = "enquiries"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    source = Column(String(50))
    service_required = Column(String(100))
    description = Column(Text)
    status = Column(Enum(EnquiryStatus), default=EnquiryStatus.NEW)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    
    customer = relationship("Customer")
    assigned_staff = relationship("User")
