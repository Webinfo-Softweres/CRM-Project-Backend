from db.session import engine, Base
from models import User, Role, Department, Customer, Enquiry
from core.security import get_password_hash


# Define all possible permissions
ALL_PERMISSIONS = [
    'customers:create',
    'customers:read',
    'customers:update',
    'customers:delete',
    'enquiries:create',
    'enquiries:read',
    'enquiries:update',
    'enquiries:delete',
    'quotations:create',
    'quotations:read',
    'quotations:update',
    'quotations:delete',
    'projects:create',
    'projects:read',
    'projects:update',
    'projects:delete',
    'tasks:create',
    'tasks:read',
    'tasks:update',
    'tasks:delete',
    'reports:create',
    'reports:read',
    'reports:update',
    'reports:delete',
    'feedback:create',
    'feedback:read',
    'feedback:update',
    'feedback:delete',
    'notifications:create',
    'notifications:read',
    'notifications:update',
    'notifications:delete',
    'users:create',
    'users:read',
    'users:update',
    'users:delete',
    'roles:create',
    'roles:read',
    'roles:update',
    'roles:delete',
    'departments:create',
    'departments:read',
    'departments:update',
    'departments:delete',
    'status_logs:create',
    'status_logs:read',
    'status_logs:update',
    'status_logs:delete',
]


MANAGER_PERMISSIONS = [
    'customers:create', 'customers:read', 'customers:update', 'customers:delete',
    'enquiries:create', 'enquiries:read', 'enquiries:update', 'enquiries:delete',
    'quotations:create', 'quotations:read', 'quotations:update', 'quotations:delete',
    'projects:create', 'projects:read', 'projects:update', 'projects:delete',
    'tasks:create', 'tasks:read', 'tasks:update', 'tasks:delete',
    'reports:read', 'reports:update', 'reports:delete',
    'feedback:create', 'feedback:read', 'feedback:update', 'feedback:delete',
    'notifications:create', 'notifications:read', 'notifications:update', 'notifications:delete',
    'status_logs:read'
]

STAFF_PERMISSIONS = [
    'customers:read',
    'enquiries:read',
    'quotations:create', 'quotations:read',
    'projects:read',
    'tasks:read', 'tasks:update',
    'reports:create', 'reports:read', 'reports:update',
    'feedback:create', 'feedback:read',
    'notifications:create', 'notifications:read', 'notifications:update', 'notifications:delete',
    'status_logs:read'
]

def init_db():
    Base.metadata.create_all(bind=engine)
    
    from db.session import SessionLocal
    db = SessionLocal()
    
    try:
        # Check if roles already exist
        admin_role = db.query(Role).filter(Role.role_name == "Admin").first()
        manager_role = db.query(Role).filter(Role.role_name == "Manager").first()
        staff_role = db.query(Role).filter(Role.role_name == "Staff").first()
        
        if not admin_role:
            admin_role = Role(role_name="Admin", description="Full system access", permissions=ALL_PERMISSIONS)
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        
        if not manager_role:
            manager_role = Role(role_name="Manager", description="Department manager", permissions=MANAGER_PERMISSIONS)
            db.add(manager_role)
            db.commit()
            db.refresh(manager_role)
        else:
            manager_role.permissions = MANAGER_PERMISSIONS
            db.commit()
        
        if not staff_role:
            staff_role = Role(role_name="Staff", description="Regular staff member", permissions=STAFF_PERMISSIONS)
            db.add(staff_role)
            db.commit()
            db.refresh(staff_role)
        else:
            staff_role.permissions = STAFF_PERMISSIONS
            db.commit()        
        # Check if departments already exist
        marketing_dept = db.query(Department).filter(Department.name == "Marketing").first()
        development_dept = db.query(Department).filter(Department.name == "Development").first()
        design_dept = db.query(Department).filter(Department.name == "Design").first()
        
        if not marketing_dept:
            marketing_dept = Department(name="Marketing", description="Digital marketing team")
            db.add(marketing_dept)
            db.commit()
            db.refresh(marketing_dept)
        
        if not development_dept:
            development_dept = Department(name="Development", description="Software development team")
            db.add(development_dept)
            db.commit()
            db.refresh(development_dept)
        
        if not design_dept:
            design_dept = Department(name="Design", description="UI/UX design team")
            db.add(design_dept)
            db.commit()
            db.refresh(design_dept)
        
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@crm.com").first()
        
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email="admin@crm.com",
                phone="1234567890",
                password=get_password_hash("admin123"),
                role_id=admin_role.id,
                department_id=marketing_dept.id,
                status="Active"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Database initialized successfully!")
            print("Default admin user created:")
            print("Email: admin@crm.com")
            print("Password: admin123")
        else:
            print("Database already initialized. Default data exists.")
        
        print("\nTables created:")
        print("- users, roles, departments")
        print("- customers, enquiries")
        print("- quotations")
        print("- projects")
        print("- tasks, task_logs")
        print("- daily_reports")
        print("- feedback")
        print("- status_logs")
        print("- notifications")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
