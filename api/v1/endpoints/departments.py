from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.user import Department
from schemas.user import Department as DepartmentSchema, DepartmentCreate
from core.security import get_current_active_user, is_admin

router = APIRouter()


@router.post("/", response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
def create_department(department: DepartmentCreate, current_user: Department = Depends(is_admin), db: Session = Depends(get_db)):
    db_dept = db.query(Department).filter(Department.name == department.name).first()
    if db_dept:
        raise HTTPException(status_code=400, detail="Department already exists")
    
    db_dept = Department(name=department.name, description=department.description)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept


@router.get("/", response_model=List[DepartmentSchema])
def get_departments(skip: int = 0, limit: int = 100, current_user: Department = Depends(get_current_active_user), db: Session = Depends(get_db)):
    departments = db.query(Department).offset(skip).limit(limit).all()
    return departments


@router.get("/{dept_id}", response_model=DepartmentSchema)
def get_department(dept_id: int, current_user: Department = Depends(get_current_active_user), db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.id == dept_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.put("/{dept_id}", response_model=DepartmentSchema)
def update_department(dept_id: int, department: DepartmentCreate, current_user: Department = Depends(is_admin), db: Session = Depends(get_db)):
    db_dept = db.query(Department).filter(Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db_dept.name = department.name
    db_dept.description = department.description
    db.commit()
    db.refresh(db_dept)
    return db_dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(dept_id: int, current_user: Department = Depends(is_admin), db: Session = Depends(get_db)):
    db_dept = db.query(Department).filter(Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(db_dept)
    db.commit()
