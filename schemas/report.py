from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class DailyReportBase(BaseModel):
    user_id: int
    report_date: date  # ISO date
    summary: Optional[str] = None
    total_hours: Decimal


class DailyReportCreate(DailyReportBase):
    pass


class DailyReportUpdate(BaseModel):
    summary: Optional[str] = None
    total_hours: Optional[Decimal] = None


class DailyReport(DailyReportBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
