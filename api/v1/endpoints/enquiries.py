from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.enquiry import Enquiry
from models.user import User
from schemas.enquiry import Enquiry as EnquirySchema, EnquiryCreate, EnquiryUpdate, EnquiryAssign, EnquiryStatusUpdate
from core.security import get_current_active_user, is_manager_or_admin, is_admin

router = APIRouter()


@router.post("/", response_model=EnquirySchema, status_code=status.HTTP_201_CREATED)
def create_enquiry(enquiry: EnquiryCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_enquiry = Enquiry(
        customer_id=enquiry.customer_id,
        source=enquiry.source,
        service_required=enquiry.service_required,
        description=enquiry.description,
        status=enquiry.status,
        assigned_to=enquiry.assigned_to
    )
    db.add(db_enquiry)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry


@router.get("/")
@router.get("")
def get_enquiries(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = db.query(Enquiry).count()
    enquiries = db.query(Enquiry).offset(skip).limit(limit).all()
    return {
        "items": enquiries,
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }


@router.get("/{enquiry_id}", response_model=EnquirySchema)
def get_enquiry(enquiry_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return enquiry


@router.put("/{enquiry_id}", response_model=EnquirySchema)
def update_enquiry(enquiry_id: int, enquiry: EnquiryUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not db_enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    update_data = enquiry.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_enquiry, field, value)
    
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry


@router.put("/{enquiry_id}/assign", response_model=EnquirySchema)
def assign_enquiry(enquiry_id: int, assignment: EnquiryAssign, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    db_enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not db_enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    assigned_user = db.query(User).filter(User.id == assignment.assigned_to).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    db_enquiry.assigned_to = assignment.assigned_to
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry


@router.put("/{enquiry_id}/status", response_model=EnquirySchema)
def update_enquiry_status(enquiry_id: int, status_update: EnquiryStatusUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not db_enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    db_enquiry.status = status_update.status
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry


@router.delete("/{enquiry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enquiry(enquiry_id: int, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not db_enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    db.delete(db_enquiry)
    db.commit()
