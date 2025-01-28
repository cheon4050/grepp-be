from datetime import datetime, timedelta
from http.client import HTTPException
from typing import List, Optional

from fastapi import FastAPI, Query, Depends
from sqlmodel import Session
from database import create_db_and_tables, get_session
from models import Reservation, AvailableTimeDTO, CreateReservationRequest, ScheduleInfo, GetReservationDTO

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/reservations/available")
def get_available_reservations(
        session: Session = Depends(get_session),
        start_time: datetime = Query(...),
        end_time: datetime = Query(...)
) -> List[AvailableTimeDTO]:
    three_days_later = datetime.now() + timedelta(days=3)

    schedules = session.query(
        ScheduleInfo
    ).filter(
        ScheduleInfo.start_time >= three_days_later,
        ScheduleInfo.start_time >= start_time,
        ScheduleInfo.end_time <= end_time,
        ScheduleInfo.max_capacity > 0
    ).all()

    available_times = [
        AvailableTimeDTO(
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            max_capacity=schedule.max_capacity
        )
        for schedule in schedules
    ]
    return available_times


@app.post("/reservations")
def create_reservation(
        request: CreateReservationRequest,
        session: Session = Depends(get_session),
):
    schedules = session.query(
        ScheduleInfo
    ).filter(
        request.start_time <= ScheduleInfo.start_time,
        request.end_time <= ScheduleInfo.end_time
    ).all()

    for schedule in schedules:
        if schedule.max_capacity < request.participants:
            raise HTTPException(
                status_code=400,
                detail="해당 시간에는 예약이 불가능합니다.",
            )

    new_reservation = Reservation(
        customer_id=request.customer_id,
        start_time=request.start_time,
        end_time=request.end_time,
        participants=request.participants,
        confirmed=False
    )

    session.add(new_reservation)
    session.commit()
    session.refresh(new_reservation)
    return "예약이 정상적으로 신청되었습니다."


@app.get("/reservations")
def get_reservations(
        customer_id: int = Query(...),
        session: Session = Depends(get_session),
):
    reservations = session.query(
        Reservation
    ).filter(
        Reservation.customer_id == customer_id
    ).all()

    reservations_dto = [
        GetReservationDTO(
            id=reservation.id,
            customer_id=reservation.customer_id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            participants=reservation.participants,
        )
        for reservation in reservations
    ]
    return reservations_dto


@app.get("/admin/reservations")
def get_reservations_admin(
        session: Session = Depends(get_session),
):
    reservations = session.query(
        Reservation
    ).all()
    reservations_dto = [
        GetReservationDTO(
            id=reservation.id,
            customer_id=reservation.customer_id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            participants=reservation.participants,
        )
        for reservation in reservations
    ]
    return reservations_dto


@app.patch("/admin/reservations")
def update_reservation_admin(
        reservation_id: int = Query(...),
        start_time: Optional[datetime] = Query(None),
        end_time: Optional[datetime] = Query(None),
        participants: Optional[int] = Query(None),
        session: Session = Depends(get_session),
):
    reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()

    if start_time:
        reservation.start_time = start_time

    if end_time:
        reservation.end_time = end_time

    schedules = session.query(ScheduleInfo).filter(
        reservation.start_time <= ScheduleInfo.start_time,
        reservation.end_time >= ScheduleInfo.end_time,
    ).all()
    if participants is not None:
        reservation.participants = participants

    for schedule in schedules:
        if schedule.max_capacity < reservation.participants:
            raise HTTPException(
                status_code=400,
                detail="해당 시간에는 예약된 인원이 많아 예약 확정이 불가능 합니다",
            )

    session.commit()

    return "예약이 정상적으로 수정되었습니다."


@app.patch("/reservations")
def update_reservation(
        customer_id: int = Query(...),
        reservation_id: int = Query(...),
        start_time: Optional[datetime] = Query(None),
        end_time: Optional[datetime] = Query(None),
        participants: Optional[int] = Query(None),
        session: Session = Depends(get_session),
):
    reservation = session.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.customer_id == customer_id
    ).first()

    if not reservation:
        raise HTTPException(
            status_code=400,
            detail="예약 수정 권한이 존재하지 않습니다.",
        )

    if start_time:
        reservation.start_time = start_time

    if end_time:
        reservation.end_time = end_time

    schedules = session.query(ScheduleInfo).filter(
        reservation.start_time <= ScheduleInfo.start_time,
        reservation.end_time >= ScheduleInfo.end_time,
    ).all()
    if participants is not None:
        reservation.participants = participants

    for schedule in schedules:
        if schedule.max_capacity < reservation.participants:
            raise HTTPException(
                status_code=400,
                detail="해당 시간에는 예약된 인원이 많아 예약 확정이 불가능 합니다",
            )

    session.commit()

    return "예약이 정상적으로 수정되었습니다."


@app.patch("/admin/reservations/confirm")
def confirm_reservation(
        reservation_id: int = Query(...),
        session: Session = Depends(get_session),
):
    reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
    schedules = session.query(ScheduleInfo).filter(
        reservation.start_time <= ScheduleInfo.start_time,
        reservation.end_time >= ScheduleInfo.end_time,
    ).all()
    for schedule in schedules:
        if schedule.max_capacity < reservation.participants:
            raise HTTPException(
                status_code=400,
                detail="해당 시간에는 예약된 인원이 많아 예약 확정이 불가능 합니다",
            )
        schedule.max_capacity -= reservation.participants

    reservation.confirmed = True
    session.commit()

    return "예약이 확정되었습니다."


@app.delete("/reservations")
def delete_reservation(
        customer_id: int = Query(...),
        reservation_id: int = Query(...),
        session: Session = Depends(get_session),
):
    reservation = session.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.customer_id == customer_id
    ).first()
    if not reservation:
        raise HTTPException(
            status_code=400,
            detail="존재하지 않거나 권한이 없는 예약 입니다.",
        )

    if reservation.confirmed == True:
        raise HTTPException(
            status_code=400,
            detail="예약 확정 후에는 취소가 불가능합니다.",
        )
    session.delete(reservation)
    session.commit()
    return "예약이 삭제되었습니다."


@app.delete("/admin/reservations")
def delete_reservation_admin(
        reservation_id: int = Query(...),
        session: Session = Depends(get_session),
):
    reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
    session.delete(reservation)
    session.commit()
    return "예약이 삭제되었습니다."
