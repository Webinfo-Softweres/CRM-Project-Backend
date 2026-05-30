# schemas/activity_log.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ActivityUserSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ActivityActionSchema(BaseModel):
    method: Optional[str] = None
    name: str


class ActivityLogItemSchema(BaseModel):
    id: int
    timestamp: datetime
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None

    user: Optional[ActivityUserSchema] = None
    action: ActivityActionSchema


class ActivityLogResponseSchema(BaseModel):
    items: list[ActivityLogItemSchema]
    total: int
    page: int
    limit: int
    pages: int