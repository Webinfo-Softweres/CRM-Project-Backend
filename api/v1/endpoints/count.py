from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from db.session import get_db

from models.user import User
from models.customer import Customer
from models.project import Project
from models.task import Task
from models.attendance import Attendance
from models.enquiry import Enquiry
from models.feedback import Feedback
from models.task import Task
from models.activity_log import ActivityLog
from models.user import User


from core.security import get_current_active_user

from utils.activity_log import create_activity_log


router = APIRouter()


@router.get("/dashboard-counts")
def get_dashboard_counts(
    request: Request,
    # current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):

    # TOTAL COUNTS

    total_staff = db.query(User).count()

    total_customers = db.query(Customer).count()

    total_projects = db.query(Project).count()

    total_tasks = db.query(Task).count()

   # PROJECT STATUS COUNTS

    completed_projects = db.query(Project).filter(
        Project.status == "Completed"
    ).count()

    ongoing_projects = db.query(Project).filter(
        Project.status == "Ongoing"
    ).count()

    hold_projects = db.query(Project).filter(
        Project.status == "Hold"
    ).count()

    # TASK STATUS COUNTS

    pending_tasks = db.query(Task).filter(
        Task.status == "Pending"
    ).count()

    inprogress_tasks = db.query(Task).filter(
        Task.status == "In Progress"
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.status == "Completed"
    ).count()

    rejected_tasks = db.query(Task).filter(
        Task.status == "Rejected"
    ).count()

    # ENQUIRY STATUS COUNTS

    new_enquiries = db.query(Enquiry).filter(
        Enquiry.status == "New"
    ).count()

    followup_enquiries = db.query(Enquiry).filter(
        Enquiry.status == "Follow-up"
    ).count()

    closed_enquiries = db.query(Enquiry).filter(
        Enquiry.status == "Closed"
    ).count()

    # FEEDBACK RATING COUNTS

    excellent_feedback = db.query(Feedback).filter(
        Feedback.rating >= 4
    ).count()

    good_feedback = db.query(Feedback).filter(
        Feedback.rating >= 3,
        Feedback.rating < 4
    ).count()

    bad_feedback = db.query(Feedback).filter(
        Feedback.rating < 3
    ).count()


    

    # TODAY ATTENDANCE

    today = date.today()

    present_employee_ids = db.query(
        Attendance.employee_id
    ).filter(
        func.date(Attendance.punch_time) == today
    ).distinct().all()

    present_count = len(present_employee_ids)

    absent_count = total_staff - present_count

    # STAFF PERFORMANCE

    staff_performance = []

    staffs = db.query(User).all()

    for staff in staffs:

        completed_tasks = db.query(Task).filter(
            Task.assigned_to == staff.id,
            Task.status == "Completed"
        ).count()

        pending_tasks = db.query(Task).filter(
            Task.assigned_to == staff.id,
            Task.status.in_(["Pending", "In Progress"])
        ).count()

        rejected_tasks = db.query(Task).filter(
            Task.assigned_to == staff.id,
            Task.status == "Rejected"
        ).count()

        total_tasks = db.query(Task).filter(
            Task.assigned_to == staff.id
        ).count()


        # ACTIVITY CRUD COUNTS

        create_count = db.query(ActivityLog).filter(
            ActivityLog.method == "POST"
        ).count()

        read_count = db.query(ActivityLog).filter(
            ActivityLog.method == "GET"
        ).count()

        update_count = db.query(ActivityLog).filter(
            ActivityLog.method == "PUT"
        ).count()

        delete_count = db.query(ActivityLog).filter(
            ActivityLog.method == "DELETE"
        ).count()

        staff_performance.append({

            "staff_id": staff.id,

            "staff_name": staff.name,

            "total_tasks": total_tasks,

            "completed_tasks": completed_tasks,

            "pending_tasks": pending_tasks,

            "rejected_tasks": rejected_tasks
        })

    # ACTIVITY LOG

    # create_activity_log(
    #     db=db,
    #     user_id=current_user.id,
    #     method="GET",
    #     action="View Dashboard Counts",
    #     endpoint="/api/v1/dashboard/dashboard-counts",
    #     ip_address=request.client.host
    # )

    return {

        "status": "success",

        "counts": {

            "total_staff": total_staff,

            "total_customers": total_customers,

            "total_projects": total_projects,

            "total_tasks": total_tasks,

            "present_staff": present_count,

            "absent_staff": absent_count
        },

        "project_status_counts": {

            "completed": completed_projects,

            "ongoing": ongoing_projects,

            # "pending": pending_projects,

            # "cancelled": cancelled_projects
            "hold":hold_projects
        },

        "task_status_counts": {

            "pending": pending_tasks,

            "in_progress": inprogress_tasks,

            "completed": completed_tasks,

            "rejected": rejected_tasks
        },
        "enquiry_status_counts": {

            "new": new_enquiries,

            "follow_up": followup_enquiries,

            "closed": closed_enquiries
        },

        "activity_log_counts": {

            "create": create_count,

            "read": read_count,

            "update": update_count,

            "delete": delete_count
        },
        "feedback_rating_counts": {

        "excellent": excellent_feedback,

        "good": good_feedback,

        "bad": bad_feedback
        },
        "staff_performance": staff_performance

            
    }