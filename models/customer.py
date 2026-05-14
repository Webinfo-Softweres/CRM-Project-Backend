from sqlalchemy import Column, Integer, String, Text
from models.base import BaseModel


class Customer(BaseModel):
    __tablename__ = "customers"
    
    name = Column(String(100), nullable=False)
    company_name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
