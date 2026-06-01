from fastapi import APIRouter, Depends, HTTPException, status,Query,Request
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models.user import User
from schemas.user import User as UserSchema, UserCreate, UserUpdate,UserResponse
from core.security import get_password_hash, get_current_active_user, is_admin
from zk import ZK
from sqlalchemy import or_
from utils.activity_log import create_activity_log



router = APIRouter()


# @router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
# def create_user(user: UserCreate, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     hashed_password = get_password_hash(user.password)
#     db_user = User(
#         name=user.name,
#         email=user.email,
#         phone=user.phone,
#         password=hashed_password,
#         role_id=user.role_id,
#         department_id=user.department_id,
#         status=user.status
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user.


DEVICE_IP = "192.168.1.201"
DEVICE_PORT = 4370


@router.post("/",response_model=UserSchema,status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate,request: Request,current_user: User = Depends(is_admin),db: Session = Depends(get_db)):


    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )


    existing_phone = db.query(User).filter(
        User.phone == user.phone
    ).first()

    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone already registered",
        )


    last_user = db.query(User).order_by(
        User.id.desc()
    ).first()

    if last_user:
        biometric_number = last_user.id + 1000

    else:
        biometric_number = 1001

    biometric_id = f"ZY{biometric_number}"


    hashed_password = get_password_hash(
        user.password
    )


    db_user = User(

        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        role_id=user.role_id,
        department_id=user.department_id,
        biometric_id=biometric_id,
    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    try:

        zk = ZK(
            DEVICE_IP,
            port=DEVICE_PORT,
            timeout=10,
        )

        conn = zk.connect()

        conn.set_user(
            uid=db_user.id,
            name=db_user.name,
            password="",
            group_id="",
            user_id=str(
                db_user.biometric_id
            ),
        )

        conn.disconnect()

    except Exception as e:

        print(
            "Biometric Sync Failed:",
            str(e)
        )


    create_activity_log(
        db=db,
        user_id=current_user.id,
        method="POST",
        action="Create User",
        endpoint="/api/v1/users",
        ip_address=request.client.host
    )

    return db_user


# @router.get("/")
# def get_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
#     total = db.query(User).count()
#     users = db.query(User).offset(skip).limit(limit).all()
#     return {
#         "items": users,
#         "total": total,
#         "page": (skip // limit) + 1 if limit else 1,
#         "limit": limit,
#         "pages": (total + limit - 1) // limit if limit else 1
#     }


# @router.get("/")
# def get_users(
#     skip: int = 0,
#     limit: int = 100,

#     # Search
#     search: str = Query(None, description="Search by name, email, phone, biometric_id"),

#     # Filters
#     role_id: int = None,
#     department_id: int = None,
#     status: str = None,
#     request: Request = None,

#     current_user: User = Depends(get_current_active_user),
#     db: Session = Depends(get_db)
# ):
#     query = db.query(User)

#     # Search
#     if search:
#         query = query.filter(
#             or_(
#                 User.name.ilike(f"%{search}%"),
#                 User.email.ilike(f"%{search}%"),
#                 User.phone.ilike(f"%{search}%"),
#                 User.biometric_id.ilike(f"%{search}%")
#             )
#         )

#     # Filters
#     if role_id:
#         query = query.filter(User.role_id == role_id)

#     if department_id:
#         query = query.filter(User.department_id == department_id)

#     if status:
#         query = query.filter(User.status == status)

#     total = query.count()

#     users = (
#         query
#         .order_by(User.id.desc())
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )


#     create_activity_log(
#         db=db,
#         user_id=current_user.id,
#         method="GET",
#         action="View Users",
#         endpoint="/api/v1/users",
#         ip_address=request.client.host if request else None
#     )


#     return {
#         "items": users,
#         "total": total,
#         "page": (skip // limit) + 1 if limit else 1,
#         "limit": limit,
#         "pages": (total + limit - 1) // limit if limit else 1
#     }



@router.get("/")
def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,

    # Search
    search: str = Query(
        None,
        description="Search by name, email, phone, biometric_id"
    ),

    # Filters
    role_id: int = None,
    department_id: int = None,
    status: str = None,

    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(User)

    # Search
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
                User.biometric_id.ilike(f"%{search}%")
            )
        )

    # Filters
    if role_id:
        query = query.filter(User.role_id == role_id)

    if department_id:
        query = query.filter(User.department_id == department_id)

    if status:
        query = query.filter(User.status == status)

    total = query.count()

    users = (
        query
        .order_by(User.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Get IP Address
    ip_address = request.headers.get("x-forwarded-for")

    if not ip_address:
        ip_address = request.client.host

    # # Activity Log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        method="GET",
        action="View Users",
        endpoint="/api/v1/users",
        ip_address=ip_address
    )

    return {
        "items": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role_id": user.role_id,
                "department_id": user.department_id,
                "status": user.status,
                "biometric_id": user.biometric_id,
                "created_at": user.created_at,
                "password": user.password
            }
            for user in users
        ],
        "total": total,
        "page": (skip // limit) + 1 if limit else 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit else 1
    }

@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, current_user: User = Depends(get_current_active_user),request: Request=None, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    create_activity_log(
        db=db,
        user_id=current_user.id,
        method="GET",
        action="View User",
        endpoint=f"/api/v1/users/{user_id}",
        ip_address=request.client.host
    )

    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserUpdate, request: Request,current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)

    create_activity_log(
        db=db,
        user_id=current_user.id,
        method="PUT",
        action="Update User",
        endpoint=f"/api/v1/users/{user_id}",
        ip_address=request.client.host
    )

    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, request: Request, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()

    create_activity_log(
        db=db,
        user_id=current_user.id,
        method="DELETE",
        action="Delete User",
        endpoint=f"/api/v1/users/{user_id}",
        ip_address=request.client.host
    )

    return None
