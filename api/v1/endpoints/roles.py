from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.user import Role
from schemas.user import Role as RoleSchema, RoleCreate
from core.security import get_current_active_user, is_admin

router = APIRouter()


@router.post("/", response_model=RoleSchema, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, current_user: Role = Depends(is_admin), db: Session = Depends(get_db)):
    db_role = db.query(Role).filter(Role.role_name == role.role_name).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    db_role = Role(
        role_name=role.role_name,
        description=role.description,
        permissions=role.permissions or []
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@router.get("/", response_model=List[RoleSchema])
def get_roles(skip: int = 0, limit: int = 100, current_user: Role = Depends(get_current_active_user), db: Session = Depends(get_db)):
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles


@router.get("/{role_id}", response_model=RoleSchema)
def get_role(role_id: int, current_user: Role = Depends(get_current_active_user), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RoleSchema)
def update_role(role_id: int, role: RoleCreate, current_user: Role = Depends(is_admin), db: Session = Depends(get_db)):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db_role.role_name = role.role_name
    db_role.description = role.description
    db_role.permissions = role.permissions or []
    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, current_user: Role = Depends(is_admin), db: Session = Depends(get_db)):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(db_role)
    db.commit()
