from fastapi import APIRouter
from sqlalchemy.orm import Session
from zk import ZK
from sqlalchemy import extract
from datetime import date,datetime

from db.session import SessionLocal
from models.attendance import Attendance
from collections import defaultdict
import calendar
from datetime import time


router = APIRouter()

DEVICE_IP = "192.168.1.201"
DEVICE_PORT = 4370


@router.post("/sync")
def sync_attendance_logs():

    db: Session = SessionLocal()

    conn = None

    try:

        print("STARTING ATTENDANCE SYNC")

        zk = ZK(
            DEVICE_IP,
            port=DEVICE_PORT,
            timeout=5,
            password=0,
            force_udp=False,
            ommit_ping=True,
        )

        print("CONNECTING DEVICE")

        conn = zk.connect()

        print("DEVICE CONNECTED")

        conn.disable_device()

        print("FETCHING USERS")

        users = list(conn.get_users())

        print(f"TOTAL USERS: {len(users)}")

        print("FETCHING ATTENDANCE LOGS")

        attendance_logs = list(conn.get_attendance())

        print(f"TOTAL LOGS FROM DEVICE: {len(attendance_logs)}")

        conn.enable_device()

        user_map = {}

        for user in users:

            user_map[str(user.user_id)] = user.name

        print("FETCHING EXISTING DATABASE RECORDS")

        existing_records = db.query(Attendance).all()

        existing_map = {

            f"{record.employee_id}_{record.punch_time}": True

            for record in existing_records
        }

        synced_data = []

        print("STARTING DATABASE SAVE")

        for log in attendance_logs:

            employee_id = str(log.user_id)

            punch_time = log.timestamp

            employee_name = user_map.get(
                employee_id,
                "Unknown"
            )

            existing_key = f"{employee_id}_{punch_time}"

            # SKIP DUPLICATES

            if existing_key in existing_map:

                continue

            attendance_record = Attendance(

                employee_id=employee_id,

                employee_name=employee_name,

                punch_time=punch_time,

                punch_type="PUNCH",
            )

            db.add(attendance_record)

            synced_data.append({

                "employee_id": attendance_record.employee_id,

                "employee_name": attendance_record.employee_name,

                "punch_time": str(attendance_record.punch_time),

                "punch_type": attendance_record.punch_type,
            })

        print("COMMITTING DATABASE")

        db.commit()

        print("SYNC COMPLETED SUCCESSFULLY")

        return {

            "status": "success",

            "total_synced": len(synced_data),

            "attendance": synced_data,
        }

    except Exception as e:

        print("ERROR:", str(e))

        db.rollback()

        return {

            "status": "error",

            "message": str(e),
        }

    finally:

        print("CLOSING CONNECTION")

        if conn:

            try:
                conn.enable_device()
            except:
                pass

            try:
                conn.disconnect()
                print("DEVICE DISCONNECTED")
            except Exception as e:
                print("DISCONNECT ERROR:", str(e))

        conn = None

        db.close()

        print("DATABASE CLOSED")


@router.get("/today")
def get_today_attendance():

    db: Session = SessionLocal()

    try:

        today = date.today()

        records = db.query(Attendance).filter(

            Attendance.punch_time >= today

        ).order_by(

            Attendance.punch_time.asc()

        ).all()

        attendance_list = []

        for record in records:

            attendance_list.append({

                "employee_id": record.employee_id,

                "employee_name": record.employee_name,

                "punch_time": str(record.punch_time),

                "punch_type": record.punch_type,
            })

        return {

            "status": "success",

            "total_punches": len(attendance_list),

            "attendance": attendance_list,
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e),
        }

    finally:

        db.close()


@router.get("/month")
def get_month_attendance(
    year: int,
    month: int,
):

    db: Session = SessionLocal()

    try:

        records = db.query(Attendance).filter(

            extract(
                "year",
                Attendance.punch_time
            ) == year,

            extract(
                "month",
                Attendance.punch_time
            ) == month,

        ).order_by(

            Attendance.punch_time.asc()

        ).all()

        attendance_list = []

        for record in records:

            attendance_list.append({

                "employee_id": record.employee_id,

                "employee_name": record.employee_name,

                "punch_time": str(record.punch_time),

                "punch_type": record.punch_type,
            })

        return {

            "status": "success",

            "year": year,

            "month": month,

            "total_punches": len(attendance_list),

            "attendance": attendance_list,
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e),
        }

    finally:

        db.close()  







# @router.get("/daily-summary")
# def get_daily_attendance(
#     attendance_date: date,
#     employee_id: str = None,
# ):

#     db: Session = SessionLocal()

#     try:

#         start_datetime = datetime.combine(
#             attendance_date,
#             datetime.min.time()
#         )

#         end_datetime = datetime.combine(
#             attendance_date,
#             datetime.max.time()
#         )

#         query = db.query(Attendance).filter(

#             Attendance.punch_time >= start_datetime,

#             Attendance.punch_time <= end_datetime
#         )

#         # FILTER USER IF PROVIDED

#         if employee_id:

#             query = query.filter(
#                 Attendance.employee_id == employee_id
#             )

#         records = query.order_by(
#             Attendance.employee_id.asc(),
#             Attendance.punch_time.asc()
#         ).all()

#         if not records:

#             return {

#                 "status": "success",

#                 "date": str(attendance_date),

#                 "attendance": []
#             }

#         grouped_data = defaultdict(list)

#         for record in records:

#             grouped_data[
#                 record.employee_id
#             ].append(record)

#         final_response = []

#         for emp_id, emp_records in grouped_data.items():

#             punches = [

#                 r.punch_time

#                 for r in emp_records
#             ]

#             sessions = []

#             break_sessions = []

#             total_work_seconds = 0

#             total_break_seconds = 0

#             for i in range(0, len(punches) - 1, 2):

#                 punch_in = punches[i]

#                 punch_out = punches[i + 1]

#                 duration = (
#                     punch_out - punch_in
#                 ).total_seconds()

#                 total_work_seconds += duration

#                 sessions.append({

#                     "punch_in": punch_in.strftime(
#                         "%Y-%m-%d %H:%M:%S"
#                     ),

#                     "punch_out": punch_out.strftime(
#                         "%Y-%m-%d %H:%M:%S"
#                     ),

#                     "work_hours": round(
#                         duration / 3600,
#                         2
#                     )
#                 })

#                 # BREAK

#                 if i + 2 < len(punches):

#                     break_start = punches[i + 1]

#                     break_end = punches[i + 2]

#                     break_duration = (
#                         break_end - break_start
#                     ).total_seconds()

#                     total_break_seconds += break_duration

#                     break_sessions.append({

#                         "break_start": break_start.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "break_end": break_end.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "break_hours": round(
#                             break_duration / 3600,
#                             2
#                         )
#                     })

#             final_response.append({

#                 "employee_id": emp_id,

#                 "employee_name": emp_records[0].employee_name,

#                 "date": str(attendance_date),

#                 "present": True,

#                 "total_work_hours": round(
#                     total_work_seconds / 3600,
#                     2
#                 ),

#                 "total_break_hours": round(
#                     total_break_seconds / 3600,
#                     2
#                 ),

#                 "sessions": sessions,

#                 "break_sessions": break_sessions
#             })

#         return {

#             "status": "success",

#             "date": str(attendance_date),

#             "total_users": len(final_response),

#             "attendance": final_response
#         }

#     except Exception as e:

#         return {

#             "status": "error",

#             "message": str(e)
#         }

#     finally:

#         db.close()


# @router.get("/monthly-summary")
# def get_monthly_attendance(
#     year: int,
#     month: int,
#     employee_id: str = None,
# ):

#     db: Session = SessionLocal()

#     try:

#         query = db.query(Attendance).filter(

#             extract(
#                 "year",
#                 Attendance.punch_time
#             ) == year,

#             extract(
#                 "month",
#                 Attendance.punch_time
#             ) == month
#         )

#         # FILTER USER IF PROVIDED

#         if employee_id:

#             query = query.filter(
#                 Attendance.employee_id == employee_id
#             )

#         records = query.order_by(
#             Attendance.employee_id.asc(),
#             Attendance.punch_time.asc()
#         ).all()

#         if not records:

#             return {

#                 "status": "success",

#                 "attendance": []
#             }

#         grouped_users = defaultdict(list)

#         for record in records:

#             grouped_users[
#                 record.employee_id
#             ].append(record)

#         final_response = []

#         for emp_id, emp_records in grouped_users.items():

#             grouped_days = defaultdict(list)

#             for record in emp_records:

#                 grouped_days[
#                     record.punch_time.date()
#                 ].append(record.punch_time)

#             present_days = len(grouped_days)

#             total_work_seconds = 0

#             daily_summary = []

#             for day, punches in grouped_days.items():

#                 punches.sort()

#                 sessions = []

#                 break_sessions = []

#                 day_work_seconds = 0

#                 day_break_seconds = 0

#                 for i in range(0, len(punches) - 1, 2):

#                     punch_in = punches[i]

#                     punch_out = punches[i + 1]

#                     duration = (
#                         punch_out - punch_in
#                     ).total_seconds()

#                     day_work_seconds += duration

#                     sessions.append({

#                         "punch_in": punch_in.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "punch_out": punch_out.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "work_hours": round(
#                             duration / 3600,
#                             2
#                         )
#                     })

#                     if i + 2 < len(punches):

#                         break_start = punches[i + 1]

#                         break_end = punches[i + 2]

#                         break_duration = (
#                             break_end - break_start
#                         ).total_seconds()

#                         day_break_seconds += break_duration

#                         break_sessions.append({

#                             "break_start": break_start.strftime(
#                                 "%Y-%m-%d %H:%M:%S"
#                             ),

#                             "break_end": break_end.strftime(
#                                 "%Y-%m-%d %H:%M:%S"
#                             ),

#                             "break_hours": round(
#                                 break_duration / 3600,
#                                 2
#                             )
#                         })

#                 total_work_seconds += day_work_seconds

#                 daily_summary.append({

#                     "date": str(day),

#                     "present": True,

#                     "total_work_hours": round(
#                         day_work_seconds / 3600,
#                         2
#                     ),

#                     "total_break_hours": round(
#                         day_break_seconds / 3600,
#                         2
#                     ),

#                     "sessions": sessions,

#                     "break_sessions": break_sessions
#                 })

#             total_days = calendar.monthrange(
#                 year,
#                 month
#             )[1]

#             absent_days = (
#                 total_days - present_days
#             )

#             final_response.append({

#                 "employee_id": emp_id,

#                 "employee_name": emp_records[0].employee_name,

#                 "year": year,

#                 "month": month,

#                 "present_days": present_days,

#                 "absent_days": absent_days,

#                 "total_work_hours": round(
#                     total_work_seconds / 3600,
#                     2
#                 ),

#                 "daily_summary": daily_summary
#             })

#         return {

#             "status": "success",

#             "total_users": len(final_response),

#             "attendance": final_response
#         }

#     except Exception as e:

#         return {

#             "status": "error",

#             "message": str(e)
#         }

#     finally:

#         db.close()




# @router.get("/daily-summary")
# def get_daily_attendance(
#     attendance_date: date,
#     employee_id: str = None,
# ):

#     db: Session = SessionLocal()

#     try:

#         office_start_time = time(9, 0)

#         half_day_limit = time(9, 30)

#         start_datetime = datetime.combine(
#             attendance_date,
#             datetime.min.time()
#         )

#         end_datetime = datetime.combine(
#             attendance_date,
#             datetime.max.time()
#         )

#         query = db.query(Attendance).filter(

#             Attendance.punch_time >= start_datetime,

#             Attendance.punch_time <= end_datetime
#         )

#         if employee_id:

#             query = query.filter(
#                 Attendance.employee_id == employee_id
#             )

#         records = query.order_by(
#             Attendance.employee_id.asc(),
#             Attendance.punch_time.asc()
#         ).all()

#         if not records:

#             return {

#                 "status": "success",

#                 "date": str(attendance_date),

#                 "attendance": []
#             }

#         grouped_data = defaultdict(list)

#         for record in records:

#             grouped_data[
#                 record.employee_id
#             ].append(record)

#         final_response = []

#         for emp_id, emp_records in grouped_data.items():

#             punches = [

#                 r.punch_time

#                 for r in emp_records
#             ]

#             punches.sort()

#             first_punch = punches[0].time()

#             if first_punch <= office_start_time:

#                 attendance_status = "Full Day"

#             else:

#                 attendance_status = "Half Day"

#             sessions = []

#             break_sessions = []

#             total_work_seconds = 0

#             total_break_seconds = 0

#             for i in range(0, len(punches) - 1, 2):

#                 punch_in = punches[i]

#                 punch_out = punches[i + 1]

#                 duration = (
#                     punch_out - punch_in
#                 ).total_seconds()

#                 total_work_seconds += duration

#                 sessions.append({

#                     "punch_in": punch_in.strftime(
#                         "%Y-%m-%d %H:%M:%S"
#                     ),

#                     "punch_out": punch_out.strftime(
#                         "%Y-%m-%d %H:%M:%S"
#                     ),

#                     "work_hours": round(
#                         duration / 3600,
#                         2
#                     )
#                 })

#                 if i + 2 < len(punches):

#                     break_start = punches[i + 1]

#                     break_end = punches[i + 2]

#                     break_duration = (
#                         break_end - break_start
#                     ).total_seconds()

#                     total_break_seconds += break_duration

#                     break_sessions.append({

#                         "break_start": break_start.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "break_end": break_end.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "break_hours": round(
#                             break_duration / 3600,
#                             2
#                         )
#                     })

#             final_response.append({

#                 "employee_id": emp_id,

#                 "employee_name": emp_records[0].employee_name,

#                 "date": str(attendance_date),

#                 "attendance_status": attendance_status,

#                 "present": True,

#                 "total_work_hours": round(
#                     total_work_seconds / 3600,
#                     2
#                 ),

#                 "total_break_hours": round(
#                     total_break_seconds / 3600,
#                     2
#                 ),

#                 "sessions": sessions,

#                 "break_sessions": break_sessions
#             })

#         return {

#             "status": "success",

#             "date": str(attendance_date),

#             "total_users": len(final_response),

#             "attendance": final_response
#         }

#     except Exception as e:

#         return {

#             "status": "error",

#             "message": str(e)
#         }

#     finally:

#         db.close()



# @router.get("/monthly-summary")
# def get_monthly_attendance(
#     year: int,
#     month: int,
#     employee_id: str = None,
# ):

#     db: Session = SessionLocal()

#     try:

#         office_start_time = time(9, 0)

#         query = db.query(Attendance).filter(

#             extract(
#                 "year",
#                 Attendance.punch_time
#             ) == year,

#             extract(
#                 "month",
#                 Attendance.punch_time
#             ) == month
#         )

#         if employee_id:

#             query = query.filter(
#                 Attendance.employee_id == employee_id
#             )

#         records = query.order_by(
#             Attendance.employee_id.asc(),
#             Attendance.punch_time.asc()
#         ).all()

#         if not records:

#             return {

#                 "status": "success",

#                 "attendance": []
#             }

#         grouped_users = defaultdict(list)

#         for record in records:

#             grouped_users[
#                 record.employee_id
#             ].append(record)

#         final_response = []

#         for emp_id, emp_records in grouped_users.items():

#             grouped_days = defaultdict(list)

#             for record in emp_records:

#                 grouped_days[
#                     record.punch_time.date()
#                 ].append(record.punch_time)

#             present_days = len(grouped_days)

#             total_work_seconds = 0

#             full_day_count = 0

#             half_day_count = 0

#             daily_summary = []

#             for day, punches in grouped_days.items():

#                 punches.sort()

#                 first_punch = punches[0].time()

#                 if first_punch <= office_start_time:

#                     attendance_status = "Full Day"

#                     full_day_count += 1

#                 else:

#                     attendance_status = "Half Day"

#                     half_day_count += 1

#                 sessions = []

#                 break_sessions = []

#                 day_work_seconds = 0

#                 day_break_seconds = 0

#                 for i in range(0, len(punches) - 1, 2):

#                     punch_in = punches[i]

#                     punch_out = punches[i + 1]

#                     duration = (
#                         punch_out - punch_in
#                     ).total_seconds()

#                     day_work_seconds += duration

#                     sessions.append({

#                         "punch_in": punch_in.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "punch_out": punch_out.strftime(
#                             "%Y-%m-%d %H:%M:%S"
#                         ),

#                         "work_hours": round(
#                             duration / 3600,
#                             2
#                         )
#                     })

#                     if i + 2 < len(punches):

#                         break_start = punches[i + 1]

#                         break_end = punches[i + 2]

#                         break_duration = (
#                             break_end - break_start
#                         ).total_seconds()

#                         day_break_seconds += break_duration

#                         break_sessions.append({

#                             "break_start": break_start.strftime(
#                                 "%Y-%m-%d %H:%M:%S"
#                             ),

#                             "break_end": break_end.strftime(
#                                 "%Y-%m-%d %H:%M:%S"
#                             ),

#                             "break_hours": round(
#                                 break_duration / 3600,
#                                 2
#                             )
#                         })

#                 total_work_seconds += day_work_seconds

#                 daily_summary.append({

#                     "date": str(day),

#                     "attendance_status": attendance_status,

#                     "present": True,

#                     "total_work_hours": round(
#                         day_work_seconds / 3600,
#                         2
#                     ),

#                     "total_break_hours": round(
#                         day_break_seconds / 3600,
#                         2
#                     ),

#                     "sessions": sessions,

#                     "break_sessions": break_sessions
#                 })

#             total_days = calendar.monthrange(
#                 year,
#                 month
#             )[1]

#             absent_days = (
#                 total_days - present_days
#             )

#             final_response.append({

#                 "employee_id": emp_id,

#                 "employee_name": emp_records[0].employee_name,

#                 "year": year,

#                 "month": month,

#                 "present_days": present_days,

#                 "full_days": full_day_count,

#                 "half_days": half_day_count,

#                 "absent_days": absent_days,

#                 "total_work_hours": round(
#                     total_work_seconds / 3600,
#                     2
#                 ),

#                 "daily_summary": daily_summary
#             })

#         return {

#             "status": "success",

#             "total_users": len(final_response),

#             "attendance": final_response
#         }

#     except Exception as e:

#         return {

#             "status": "error",

#             "message": str(e)
#         }

#     finally:

#         db.close()




from collections import defaultdict
from datetime import datetime, date, time
from sqlalchemy import extract
import calendar


@router.get("/daily-summary")
def get_daily_attendance(
    attendance_date: date,
    employee_id: str = None,
):

    db: Session = SessionLocal()

    try:

        office_start_time = time(9, 30)

        start_datetime = datetime.combine(
            attendance_date,
            datetime.min.time()
        )

        end_datetime = datetime.combine(
            attendance_date,
            datetime.max.time()
        )

        query = db.query(Attendance).filter(

            Attendance.punch_time >= start_datetime,

            Attendance.punch_time <= end_datetime
        )

        if employee_id:

            query = query.filter(
                Attendance.employee_id == employee_id
            )

        records = query.order_by(
            Attendance.employee_id.asc(),
            Attendance.punch_time.asc()
        ).all()

        if not records:

            return {

                "status": "success",

                "date": str(attendance_date),

                "attendance": []
            }

        grouped_data = defaultdict(list)

        for record in records:

            grouped_data[
                record.employee_id
            ].append(record)

        final_response = []

        for emp_id, emp_records in grouped_data.items():

            punches = [

                r.punch_time

                for r in emp_records
            ]

            punches.sort()

            # FIRST PUNCH = IN

            first_punch = punches[0]

            # LAST PUNCH = OUT

            last_punch = punches[-1]

            # MIDDLE PUNCHES = BREAKS

            middle_punches = punches[1:-1]

            break_sessions = []

            total_break_seconds = 0

            for i in range(0, len(middle_punches), 2):

                if i + 1 < len(middle_punches):

                    break_start = middle_punches[i]

                    break_end = middle_punches[i + 1]

                    break_duration = (
                        break_end - break_start
                    ).total_seconds()

                    total_break_seconds += break_duration

                    break_sessions.append({

                        "break_start": break_start.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                        "break_end": break_end.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                        "break_hours": round(
                            break_duration / 3600,
                            2
                        )
                    })

            # TOTAL OFFICE TIME

            office_duration = (
                last_punch - first_punch
            ).total_seconds()

            # ACTUAL WORK TIME

            actual_work_seconds = (
                office_duration - total_break_seconds
            )

            actual_work_hours = round(
                actual_work_seconds / 3600,
                2
            )

            # ATTENDANCE STATUS

            if first_punch.time() <= office_start_time:

                attendance_status = "Full Day"

            else:

                attendance_status = "Half Day"

            sessions = [{

                "punch_in": first_punch.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "punch_out": last_punch.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "work_hours": actual_work_hours
            }]

            final_response.append({

                "employee_id": emp_id,

                "employee_name": emp_records[0].employee_name,

                "date": str(attendance_date),

                "attendance_status": attendance_status,

                "present": True,

                "total_work_hours": actual_work_hours,

                "total_break_hours": round(
                    total_break_seconds / 3600,
                    2
                ),

                "sessions": sessions,

                "break_sessions": break_sessions
            })

        return {

            "status": "success",

            "date": str(attendance_date),

            "total_users": len(final_response),

            "attendance": final_response
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)
        }

    finally:

        db.close()



@router.get("/monthly-summary")
def get_monthly_attendance(
    year: int,
    month: int,
    employee_id: str = None,
):

    db: Session = SessionLocal()

    try:

        office_start_time = time(9, 30)

        query = db.query(Attendance).filter(

            extract(
                "year",
                Attendance.punch_time
            ) == year,

            extract(
                "month",
                Attendance.punch_time
            ) == month
        )

        if employee_id:

            query = query.filter(
                Attendance.employee_id == employee_id
            )

        records = query.order_by(
            Attendance.employee_id.asc(),
            Attendance.punch_time.asc()
        ).all()

        if not records:

            return {

                "status": "success",

                "attendance": []
            }

        grouped_users = defaultdict(list)

        for record in records:

            grouped_users[
                record.employee_id
            ].append(record)

        final_response = []

        for emp_id, emp_records in grouped_users.items():

            grouped_days = defaultdict(list)

            for record in emp_records:

                grouped_days[
                    record.punch_time.date()
                ].append(record.punch_time)

            present_days = 0

            full_day_count = 0

            half_day_count = 0

            total_work_seconds = 0

            daily_summary = []

            for day, punches in grouped_days.items():

                punches.sort()

                first_punch = punches[0]

                last_punch = punches[-1]

                middle_punches = punches[1:-1]

                break_sessions = []

                total_break_seconds = 0

                for i in range(0, len(middle_punches), 2):

                    if i + 1 < len(middle_punches):

                        break_start = middle_punches[i]

                        break_end = middle_punches[i + 1]

                        break_duration = (
                            break_end - break_start
                        ).total_seconds()

                        total_break_seconds += break_duration

                        break_sessions.append({

                            "break_start": break_start.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),

                            "break_end": break_end.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),

                            "break_hours": round(
                                break_duration / 3600,
                                2
                            )
                        })

                office_duration = (
                    last_punch - first_punch
                ).total_seconds()

                actual_work_seconds = (
                    office_duration - total_break_seconds
                )

                actual_work_hours = round(
                    actual_work_seconds / 3600,
                    2
                )

                total_work_seconds += actual_work_seconds

                # ATTENDANCE STATUS

                if first_punch.time() <= office_start_time:

                    attendance_status = "Full Day"

                    full_day_count += 1

                else:

                    attendance_status = "Half Day"

                    half_day_count += 1

                present_days += 1

                sessions = [{

                    "punch_in": first_punch.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "punch_out": last_punch.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "work_hours": actual_work_hours
                }]

                daily_summary.append({

                    "date": str(day),

                    "attendance_status": attendance_status,

                    "present": True,

                    "total_work_hours": actual_work_hours,

                    "total_break_hours": round(
                        total_break_seconds / 3600,
                        2
                    ),

                    "sessions": sessions,

                    "break_sessions": break_sessions
                })

            total_days = calendar.monthrange(
                year,
                month
            )[1]

            absent_days = (
                total_days - present_days
            )

            final_response.append({

                "employee_id": emp_id,

                "employee_name": emp_records[0].employee_name,

                "year": year,

                "month": month,

                "present_days": present_days,

                "full_days": full_day_count,

                "half_days": half_day_count,

                "absent_days": absent_days,

                "total_work_hours": round(
                    total_work_seconds / 3600,
                    2
                ),

                "daily_summary": daily_summary
            })

        return {

            "status": "success",

            "total_users": len(final_response),

            "attendance": final_response
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)
        }

    finally:

        db.close()
