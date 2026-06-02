from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, String

from typing import List
from db.session import get_db
from models.report import DailyReport
from models.user import User
from schemas.report import DailyReport as DailyReportSchema, DailyReportCreate, DailyReportUpdate
from core.security import get_current_active_user
from datetime import datetime
import pytz
from datetime import timezone
from zoneinfo import ZoneInfo

IST = pytz.timezone("Asia/Kolkata")


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
        total_hours=report.total_hours,
        created_at=datetime.now(IST)
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


# @router.get("/")
# def get_daily_reports(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
#     total = db.query(DailyReport).count()
#     reports = db.query(DailyReport).offset(skip).limit(limit).all()
#     return {
#         "items": reports,
#         "total": total,
#         "page": (skip // limit) + 1 if limit else 1,
#         "limit": limit,
#         "pages": (total + limit - 1) // limit if limit else 1
#     }


@router.get("/")
def get_daily_reports(
    skip: int = 0,
    limit: int = 100,

    # Search
    search: str = Query(
        None,
        description="Search by summary, total hours, or report date"
    ),

    # Filters
    user_id: int = None,
    report_date: str = None,
    total_hours: int = None,

    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(DailyReport)

    # Search
    if search:
        query = query.filter(
            or_(
                DailyReport.summary.ilike(f"%{search}%"),
                DailyReport.report_date.cast(String).ilike(f"%{search}%"),
                DailyReport.total_hours.cast(String).ilike(f"%{search}%")
            )
        )

    # Filters
    if user_id:
        query = query.filter(
            DailyReport.user_id == user_id
        )

    if report_date:
        query = query.filter(
            DailyReport.report_date.cast(String).ilike(f"%{report_date}%")
        )

    if total_hours:
        query = query.filter(
            DailyReport.total_hours == total_hours
        )

    total = query.count()

    reports = (
        query
        .order_by(DailyReport.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    for report in reports:
        if report.created_at:
            report.created_at = report.created_at.replace(
                tzinfo=timezone.utc
            ).astimezone(IST)


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
