from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Canteen information
    store_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    canteen_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    prediction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Calendar inputs
    is_state_holiday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_school_holiday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_special_day: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Automatically retrieved weather
    temperature_max: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    temperature_min: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    temperature_mean: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sunshine_sum: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    precipitation_sum: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Historical scaled features used by the current ML model
    sales_lag_1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sales_lag_7: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sales_rolling_mean_7: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Raw ML output
    scaled_prediction: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Operational output
    expected_portions: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    safety_buffer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    recommended_portions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Actual end-of-day result
    actual_portions: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    absolute_error: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # MLOps traceability
    model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    calibration_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    actual_recorded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )