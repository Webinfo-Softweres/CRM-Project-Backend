from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.project import Project
from models.customer import Customer
from models.quotation import Quotation
from models.user import User
from schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate, ProjectStatusUpdate
from core.security import get_current_active_user, is_manager_or_admin, is_admin

router = APIRouter()


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == project.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if quotation exists and is confirmed
    quotation = db.query(Quotation).filter(Quotation.id == project.quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quotation.status != "Confirmed":
        raise HTTPException(status_code=400, detail="Only confirmed quotations can create projects")
    
    db_project = Project(
        customer_id=project.customer_id,
        quotation_id=project.quotation_id,
        project_name=project.project_name,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/")
@router.get("")
def get_projects(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total = db.query(Project).count()
    projects = db.query(Project).offset(skip).limit(limit).all()
    return {
        "items": projects,
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }


@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(project_id: int, project: ProjectUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


@router.put("/{project_id}/status", response_model=ProjectSchema)
def update_project_status(project_id: int, status_update: ProjectStatusUpdate, current_user: User = Depends(is_manager_or_admin), db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.status = status_update.status
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
