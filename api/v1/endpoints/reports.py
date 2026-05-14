from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.report import DailyReport
from models.user import User
from schemas.report import DailyReport as DailyReportSchema, DailyReportCreate, DailyReportUpdate
from core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=DailyReportSchema, status_code=status.HTTP_201_CREATED)
def create_daily_report(report: DailyReportCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == report.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_report = DailyReport(
        user_id=report.user_id,
        report_date=report.report_date,
        summary=report.summary,
        total_hours=report.total_hours
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/")
def get_daily_reports(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = db.query(DailyReport).count()
    reports = db.query(DailyReport).offset(skip).limit(limit).all()
    return {
        "items": reports,
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }


@router.get("/user/{user_id}", response_model=List[DailyReportSchema])
def get_reports_by_user(user_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    reports = db.query(DailyReport).filter(DailyReport.user_id == user_id).all()
    return reports


@router.get("/{report_id}", response_model=DailyReportSchema)
def get_daily_report(report_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=DailyReportSchema)
def update_daily_report(report_id: int, report: DailyReportUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    update_data = report.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daily_report(report_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(db_report)
    db.commit()
