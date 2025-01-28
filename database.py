from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine
from models import ScheduleInfo, Admin, Customer

DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    db = SessionLocal()  # DB 세션을 생성하는 코드
    try:
        yield db
    finally:
        db.close()


# 30분 단위로 예약이 가능하게 하기 위해 30분 단위의 테이블을 생성하였습니다.
def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        start_time = datetime(2025, 1, 1, 0, 0)
        end_time = datetime(2026, 1, 1, 0, 0)
        while start_time < end_time:
            session.add(
                ScheduleInfo(
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=30),
                    max_capacity=50000,
                )
            )
            start_time += timedelta(minutes=30)
        session.add(Customer())
        session.add(Admin())
        session.commit()

