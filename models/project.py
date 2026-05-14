from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class ProjectStatus(str, enum.Enum):
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    HOLD = "Hold"


class Project(BaseModel):
    __tablename__ = "projects"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    project_name = Column(String(200), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ONGOING)
    
    customer = relationship("Customer")
    quotation = relationship("Quotation")
