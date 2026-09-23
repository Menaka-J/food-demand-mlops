from sqlalchemy import Column, Integer, Float, String, Date

from .database import Base


class DailyRecord(Base):
    __tablename__ = "daily_records"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, nullable=False)
    store = Column(String, nullable=False)

    is_state_holiday = Column(String, nullable=False)
    is_school_holiday = Column(String, nullable=False)
    is_special_day = Column(String, nullable=False)

    temperature_max = Column(Float)
    temperature_min = Column(Float)
    temperature_mean = Column(Float)

    sunshine_sum = Column(Float)
    precipitation_sum = Column(Float)

    actual_sales = Column(Float, nullable=True)
    prediction = Column(Float, nullable=True)