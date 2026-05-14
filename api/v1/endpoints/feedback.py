from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.feedback import Feedback
from models.customer import Customer
from models.project import Project
from models.user import User
from schemas.feedback import Feedback as FeedbackSchema, FeedbackCreate, FeedbackUpdate
from core.security import get_current_active_user, is_admin

router = APIRouter()


@router.post("/", response_model=FeedbackSchema, status_code=status.HTTP_201_CREATED)
def create_feedback(feedback: FeedbackCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == feedback.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == feedback.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate rating (1-5)
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    db_feedback = Feedback(
        customer_id=feedback.customer_id,
        project_id=feedback.project_id,
        rating=feedback.rating,
        comments=feedback.comments
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@router.get("/", response_model=List[FeedbackSchema])
def get_feedback(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    feedback_list = db.query(Feedback).offset(skip).limit(limit).all()
    return feedback_list


@router.get("/project/{project_id}", response_model=List[FeedbackSchema])
def get_feedback_by_project(project_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    feedback_list = db.query(Feedback).filter(Feedback.project_id == project_id).all()
    return feedback_list


@router.get("/{feedback_id}", response_model=FeedbackSchema)
def get_feedback(feedback_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackSchema)
def update_feedback(feedback_id: int, feedback: FeedbackUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    update_data = feedback.dict(exclude_unset=True)
    
    # Validate rating if provided
    if "rating" in update_data:
        if update_data["rating"] < 1 or update_data["rating"] > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    for field, value in update_data.items():
        setattr(db_feedback, field, value)
    
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(feedback_id: int, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    db.delete(db_feedback)
    db.commit()
