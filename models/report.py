from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel


class DailyReport(BaseModel):
    __tablename__ = "daily_reports"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_date = Column(Date, nullable=False)  # Store as DATE
    summary = Column(Text)
    total_hours = Column(Numeric(5, 2), nullable=False)
    
    user = relationship("User")
