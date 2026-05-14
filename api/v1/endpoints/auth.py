from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User, Role
from schemas.user import Token, UserCreate, LoginRequest
from core.security import verify_password, get_password_hash, create_access_token, get_current_active_user
from datetime import timedelta
from core.config import settings

router = APIRouter()


@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get role name
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.role_name.lower() if role else 'staff'
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": role_name,
            "role_id": user.role_id,
            "department_id": user.department_id,
            "status": user.status,
            "is_active": user.status == 'active',
            "created_at": user.created_at
        }
    }


@router.get("/me")
def get_current_user(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Get role name
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    role_name = role.role_name.lower() if role else 'staff'
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": role_name,
        "role_id": current_user.role_id,
        "department_id": current_user.department_id,
        "status": current_user.status,
        "is_active": current_user.status == 'active',
        "created_at": current_user.created_at
    }


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        role_id=user.role_id,
        department_id=user.department_id,
        status=user.status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Get role name
    role = db.query(Role).filter(Role.id == db_user.role_id).first()
    role_name = role.role_name.lower() if role else 'staff'
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone,
            "role": role_name,
            "role_id": db_user.role_id,
            "department_id": db_user.department_id,
            "status": db_user.status,
            "is_active": db_user.status == 'active',
            "created_at": db_user.created_at
        }
    }
