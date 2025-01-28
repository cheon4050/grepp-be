from datetime import datetime, timedelta

from pydantic import BaseModel
from pydantic.v1 import validator
from sqlmodel import Field, SQLModel, Column, BigInteger


class Customer(SQLModel, table=True):
    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )


class Admin(SQLModel, table=True):
    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )


class ScheduleInfo(SQLModel, table=True):
    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    start_time: datetime
    end_time: datetime
    max_capacity: int


class Reservation(SQLModel, table=True):
    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    customer_id: int = Field(foreign_key="customer.id")
    start_time: datetime
    end_time: datetime
    participants: int
    confirmed: bool = Field(default=False)

class GetReservationDTO(BaseModel):
    id: int
    customer_id: int
    start_time: datetime
    end_time: datetime
    participants: int

class AvailableTimeDTO(BaseModel):
    start_time: datetime
    end_time: datetime
    max_capacity: int


class CreateReservationRequest(BaseModel):
    customer_id: int
    start_time: datetime
    end_time: datetime
    participants: int

    @validator("start_time")
    def validate_start_time(self, start_time):
        if start_time < datetime.now() + timedelta(days=3):
            raise ValueError("예약은 3일 전까지 가능 합니다.")
        return start_time
