from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel


class StatusLog(BaseModel):
    __tablename__ = "status_logs"
    
    module = Column(String(50), nullable=False)  # enquiry, quotation, task, project
    record_id = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=True)
    
    user = relationship("User")
