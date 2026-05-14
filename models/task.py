from sqlalchemy import Column, Integer, String, Text, Numeric, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
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


class Task(BaseModel):
    __tablename__ = "tasks"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    department_id = Column(Integer, ForeignKey("departments.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    estimated_hours = Column(Numeric(5, 2))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    project = relationship("Project")
    department = relationship("Department")
    assigned_staff = relationship("User")


class TaskLog(BaseModel):
    __tablename__ = "task_logs"
    
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False)  # Store as DATE
    hours_spent = Column(Numeric(5, 2), nullable=False)
    description = Column(Text)
    
    task = relationship("Task")
    user = relationship("User")
