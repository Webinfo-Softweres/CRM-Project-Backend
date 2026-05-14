from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
import enum


class QuotationStatus(str, enum.Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CONFIRMED = "Confirmed"


class QuotationBase(BaseModel):
    enquiry_id: int
    amount: Decimal
    description: Optional[str] = None
    status: QuotationStatus = QuotationStatus.DRAFT
    created_by: Optional[int] = None


class QuotationCreate(QuotationBase):
    pass


class QuotationUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    status: Optional[QuotationStatus] = None


class QuotationApprove(BaseModel):
    approved_by: int


class Quotation(QuotationBase):
    id: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
