from fastapi import APIRouter
from api.v1.endpoints import auth, users, roles, departments, customers, enquiries, quotations, projects, tasks, reports, feedback, status_logs, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(enquiries.router, prefix="/enquiries", tags=["enquiries"])
api_router.include_router(quotations.router, prefix="/quotations", tags=["quotations"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(status_logs.router, prefix="/status-logs", tags=["status-logs"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
