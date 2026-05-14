from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from db.session import Base


class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
