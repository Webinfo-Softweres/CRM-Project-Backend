from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import enum


class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None
    permissions: Optional[list[str]] = []


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class Department(DepartmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str
