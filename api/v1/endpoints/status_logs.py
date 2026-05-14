from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from db.session import get_db
from models.status_log import StatusLog
from models.user import User
from schemas.status_log import StatusLog as StatusLogSchema, StatusLogCreate
from core.security import get_current_active_user, is_admin

router = APIRouter()


@router.post("/", response_model=StatusLogSchema, status_code=status.HTTP_201_CREATED)
def create_status_log(log: StatusLogCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == log.changed_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_log = StatusLog(
        module=log.module,
        record_id=log.record_id,
        status=log.status,
        changed_by=log.changed_by,
        changed_at=datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/", response_model=List[StatusLogSchema])
def get_status_logs(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    logs = db.query(StatusLog).offset(skip).limit(limit).all()
    return logs


@router.get("/module/{module_name}", response_model=List[StatusLogSchema])
def get_status_logs_by_module(module_name: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    logs = db.query(StatusLog).filter(StatusLog.module == module_name).all()
    return logs


@router.get("/record/{module_name}/{record_id}", response_model=List[StatusLogSchema])
def get_status_logs_by_record(module_name: str, record_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    logs = db.query(StatusLog).filter(
        StatusLog.module == module_name,
        StatusLog.record_id == record_id
    ).all()
    return logs


@router.get("/{log_id}", response_model=StatusLogSchema)
def get_status_log(log_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    log = db.query(StatusLog).filter(StatusLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Status log not found")
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status_log(log_id: int, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_log = db.query(StatusLog).filter(StatusLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Status log not found")
    
    db.delete(db_log)
    db.commit()
