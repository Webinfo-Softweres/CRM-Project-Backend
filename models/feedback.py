from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Feedback(BaseModel):
    __tablename__ = "feedback"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comments = Column(Text)
    
    customer = relationship("Customer")
    project = relationship("Project")
