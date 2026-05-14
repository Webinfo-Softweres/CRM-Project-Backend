from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackBase(BaseModel):
    customer_id: int
    project_id: int
    rating: int  # 1-5
    comments: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = None
    comments: Optional[str] = None


class Feedback(FeedbackBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
