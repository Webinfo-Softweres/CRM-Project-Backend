from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class QuotationStatus(str, enum.Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CONFIRMED = "Confirmed"


class Quotation(BaseModel):
    __tablename__ = "quotations"
    
    enquiry_id = Column(Integer, ForeignKey("enquiries.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    status = Column(Enum(QuotationStatus), default=QuotationStatus.DRAFT)
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime, nullable=True)
    
    enquiry = relationship("Enquiry")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
