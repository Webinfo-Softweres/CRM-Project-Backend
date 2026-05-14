from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    REJECTED = "Rejected"


class TaskPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskBase(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    department_id: Optional[int] = None
    assigned_to: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None
    assigned_to: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskAssign(BaseModel):
    assigned_to: int


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskLogBase(BaseModel):
    task_id: int
    user_id: int
    work_date: date  # ISO date
    hours_spent: Decimal
    description: Optional[str] = None


class TaskLogCreate(TaskLogBase):
    pass


class TaskLog(TaskLogBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Task(TaskBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
