from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, String

from typing import List
from datetime import datetime
from db.session import get_db
from models.quotation import Quotation
from models.user import User
from models.enquiry import Enquiry
from schemas.quotation import Quotation as QuotationSchema, QuotationCreate, QuotationUpdate, QuotationApprove
from core.security import get_current_active_user, is_manager_or_admin, is_admin

router = APIRouter()


@router.post("/", response_model=QuotationSchema, status_code=status.HTTP_201_CREATED)
def create_quotation(quotation: QuotationCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if enquiry exists
    enquiry = db.query(Enquiry).filter(Enquiry.id == quotation.enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    db_quotation = Quotation(
        enquiry_id=quotation.enquiry_id,
        amount=quotation.amount,
        description=quotation.description,
        status=quotation.status,
        created_by=quotation.created_by
    )
    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)
    return db_quotation


# @router.get("/")
# def get_quotations(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
#     total = db.query(Quotation).count()
#     quotations = db.query(Quotation).offset(skip).limit(limit).all()
#     return {
#         "items": quotations,
#         "total": total,
#         "page": (skip // limit) + 1 if limit else 1,
#         "limit": limit,
#         "pages": (total + limit - 1) // limit if limit else 1
#     }


@router.get("/")
def get_quotations(
    skip: int = 0,
    limit: int = 100,

    # Search
    search: str = Query(
        None,
        description="Search by title, description, status, or amount"
    ),

    # Filters
    status: str = None,
    # customer_id: int = None,
    enquiry_id: int = None,
    created_by: int = None,

    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Quotation)

    # Search
    if search:
        query = query.filter(
            or_(
                # Quotation.title.ilike(f"%{search}%"),
                Quotation.description.ilike(f"%{search}%"),
                Quotation.status.cast(String).ilike(f"%{search}%"),
                Quotation.amount.cast(String).ilike(f"%{search}%")
            )
        )

    # Filters
    if status:
        query = query.filter(
            Quotation.status.cast(String).ilike(f"%{status}%")
        )

    # if customer_id:
    #     query = query.filter(
    #         Quotation.customer_id == customer_id
    #     )

    if enquiry_id:
        query = query.filter(
            Quotation.enquiry_id == enquiry_id
        )

    if created_by:
        query = query.filter(
            Quotation.created_by == created_by
        )

    total = query.count()

    quotations = (
        query
        .order_by(Quotation.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": quotations,
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }

@router.get("/{quotation_id}", response_model=QuotationSchema)
def get_quotation(quotation_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.put("/{quotation_id}", response_model=QuotationSchema)
def update_quotation(quotation_id: int, quotation: QuotationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    update_data = quotation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_quotation, field, value)
    
    db.commit()
    db.refresh(db_quotation)
    return db_quotation


@router.put("/{quotation_id}/approve", response_model=QuotationSchema)
def approve_quotation(quotation_id: int, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    db_quotation.status = "Approved"
    db_quotation.approved_by = current_user.id
    db_quotation.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(db_quotation)
    return db_quotation


@router.put("/{quotation_id}/reject", response_model=QuotationSchema)
def reject_quotation(quotation_id: int, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    db_quotation.status = "Rejected"
    db_quotation.approved_by = current_user.id
    db_quotation.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(db_quotation)
    return db_quotation


@router.put("/{quotation_id}/confirm", response_model=QuotationSchema)
def confirm_quotation(quotation_id: int, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if db_quotation.status != "Approved":
        raise HTTPException(status_code=400, detail="Only approved quotations can be confirmed")
    
    db_quotation.status = "Confirmed"
    db.commit()
    db.refresh(db_quotation)
    return db_quotation


@router.delete("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation(quotation_id: int, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    db.delete(db_quotation)
    db.commit()
