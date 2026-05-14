from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.task import Task, TaskLog
from models.project import Project
from models.user import User, Department
from schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate, TaskAssign, TaskStatusUpdate, TaskLog as TaskLogSchema, TaskLogCreate
from core.security import get_current_active_user, is_manager_or_admin, is_admin

router = APIRouter()


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if project exists
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if assigned user exists
    if task.assigned_to:
        user = db.query(User).filter(User.id == task.assigned_to).first()
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")
    
    # Check if department exists
    if task.department_id:
        department = db.query(Department).filter(Department.id == task.department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
    
    db_task = Task(
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        department_id=task.department_id,
        assigned_to=task.assigned_to,
        estimated_hours=task.estimated_hours,
        status=task.status,
        priority=task.priority
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/")
@router.get("")
def get_tasks(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = db.query(Task).count()
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return {
        "items": tasks,
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }


@router.get("/project/{project_id}", response_model=List[TaskSchema])
def get_tasks_by_project(project_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks


@router.get("/{task_id}", response_model=TaskSchema)
def get_task(task_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@router.put("/{task_id}/assign", response_model=TaskSchema)
def assign_task(task_id: int, assignment: TaskAssign, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    assigned_user = db.query(User).filter(User.id == assignment.assigned_to).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    db_task.assigned_to = assignment.assigned_to
    db.commit()
    db.refresh(db_task)
    return db_task


@router.put("/{task_id}/status", response_model=TaskSchema)
def update_task_status(task_id: int, status_update: TaskStatusUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.status = status_update.status
    db.commit()
    db.refresh(db_task)
    return db_task


@router.post("/{task_id}/log-hours", response_model=TaskLogSchema, status_code=status.HTTP_201_CREATED)
def log_task_hours(task_id: int, log: TaskLogCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user exists
    user = db.query(User).filter(User.id == log.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_log = TaskLog(
        task_id=log.task_id,
        user_id=log.user_id,
        work_date=log.work_date,
        hours_spent=log.hours_spent,
        description=log.description
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/{task_id}/logs", response_model=List[TaskLogSchema])
def get_task_logs(task_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    logs = db.query(TaskLog).filter(TaskLog.task_id == task_id).all()
    return logs


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
