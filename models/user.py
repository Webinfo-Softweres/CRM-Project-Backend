from sqlalchemy import Column, Integer, String, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class User(BaseModel):
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    
    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")


class Role(BaseModel):
    __tablename__ = "roles"

    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(JSON, default=list)

    users = relationship("User", back_populates="role")


class Department(BaseModel):
    __tablename__ = "departments"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    
    users = relationship("User", back_populates="department")
