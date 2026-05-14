from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StatusLogBase(BaseModel):
    module: str
    record_id: int
    status: str
    changed_by: int


class StatusLogCreate(StatusLogBase):
    pass


class StatusLog(StatusLogBase):
    id: int
    changed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
