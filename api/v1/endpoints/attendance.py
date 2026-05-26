from fastapi import APIRouter
from sqlalchemy.orm import Session
from zk import ZK
from sqlalchemy import extract
from datetime import date,datetime

from db.session import SessionLocal
from models.attendance import Attendance


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


# @router.delete("/clear-device")
# def clear_device_attendance():

#     conn = None

#     try:

#         print("CONNECTING DEVICE")

#         zk = ZK(
#             DEVICE_IP,
#             port=DEVICE_PORT,
#             timeout=5,
#             password=0,
#             force_udp=False,
#             ommit_ping=True,
#         )

#         conn = zk.connect()

#         print("DEVICE CONNECTED")

#         conn.disable_device()

#         # CLEAR ATTENDANCE LOGS FROM DEVICE

#         conn.clear_attendance()

#         conn.enable_device()

#         print("DEVICE ATTENDANCE CLEARED")

#         return {

#             "status": "success",

#             "message": "All attendance logs cleared from punching machine",
#         }

#     except Exception as e:

#         print("ERROR:", str(e))

#         return {

#             "status": "error",

#             "message": str(e),
#         }

#     finally:

#         if conn:

#             try:
#                 conn.enable_device()
#             except:
#                 pass

#             try:
#                 conn.disconnect()
#             except:
#                 pass



# @router.delete("/clear-device-users")
# def clear_device_users():

#     conn = None

#     try:

#         print("CONNECTING DEVICE")

#         zk = ZK(
#             DEVICE_IP,
#             port=DEVICE_PORT,
#             timeout=5,
#             password=0,
#             force_udp=False,
#             ommit_ping=True,
#         )

#         conn = zk.connect()

#         print("DEVICE CONNECTED")

#         conn.disable_device()

#         users = list(conn.get_users())

#         deleted_users = []

#         for user in users:

#             # SKIP SUPER ADMIN

#             if user.privilege == 14:
#                 continue

#             try:

#                 conn.delete_user(uid=user.uid)

#                 deleted_users.append({

#                     "uid": user.uid,

#                     "user_id": user.user_id,

#                     "name": user.name,
#                 })

#                 print(f"DELETED USER: {user.name}")

#             except Exception as e:

#                 print(f"FAILED TO DELETE {user.name}: {e}")

#         conn.enable_device()

#         return {

#             "status": "success",

#             "message": "All normal users deleted from device",

#             "deleted_count": len(deleted_users),

#             "deleted_users": deleted_users,
#         }

#     except Exception as e:

#         print("ERROR:", str(e))

#         return {

#             "status": "error",

#             "message": str(e),
#         }

#     finally:

#         if conn:

#             try:
#                 conn.enable_device()
#             except:
#                 pass

#             try:
#                 conn.disconnect()
#             except:
#                 pass



# @router.delete("/clear")
# def clear_attendance_data():

#     db: Session = SessionLocal()

#     try:

#         deleted_count = db.query(Attendance).delete()

#         db.commit()

#         return {

#             "status": "success",

#             "message": "All attendance records deleted successfully",

#             "total_deleted": deleted_count,
#         }

#     except Exception as e:

#         db.rollback()

#         return {

#             "status": "error",

#             "message": str(e),
#         }

#     finally:

#         db.close()