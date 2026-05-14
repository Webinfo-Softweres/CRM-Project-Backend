from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import enum


class ProjectStatus(str, enum.Enum):
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    HOLD = "Hold"


class ProjectBase(BaseModel):
    customer_id: int
    quotation_id: int
    project_name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.ONGOING


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ProjectStatus] = None


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatus


class Project(ProjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
