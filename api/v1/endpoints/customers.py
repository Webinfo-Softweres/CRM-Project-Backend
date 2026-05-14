from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db.session import get_db
from models.customer import Customer
from models.user import User
from schemas.customer import Customer as CustomerSchema, CustomerCreate, CustomerUpdate
from core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_customer = Customer(
        name=customer.name,
        company_name=customer.company_name,
        phone=customer.phone,
        email=customer.email,
        address=customer.address
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/")
@router.get("")
def get_customers(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    total = db.query(Customer).count()
    return {
        "items": customers,
        "page": (skip // limit) + 1,
        "limit": limit,
        "total": total
    }


@router.get("/{customer_id}", response_model=CustomerSchema)
def get_customer(customer_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerSchema)
def update_customer(customer_id: int, customer: CustomerUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(db_customer)
    db.commit()
