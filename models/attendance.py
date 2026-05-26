from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Float,
)

from db.session import Base


class Attendance(Base):

    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    employee_id = Column(String(50))

    employee_name = Column(String(100))

    punch_time = Column(DateTime)

    punch_type = Column(String(20), default="PUNCH")

