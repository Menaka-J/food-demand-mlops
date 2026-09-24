from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    store_id: str
    prediction_date: date

    is_state_holiday: bool = False
    is_school_holiday: bool = False
    is_special_day: bool = False


class ActualRequest(BaseModel):
    actual_portions: int = Field(
        ge=0,
        description="Actual number of portions sold."
    )


class PredictionResponse(BaseModel):
    record_id: int

    store_id: str
    canteen_name: str
    city: str
    state: str

    prediction_date: date

    is_state_holiday: bool
    is_school_holiday: bool
    is_special_day: bool

    temperature_max: float
    temperature_min: float
    temperature_mean: float
    sunshine_sum: float
    precipitation_sum: float

    scaled_prediction: float

    expected_portions: float
    safety_buffer: int
    recommended_portions: int

    model_version: str
    calibration_version: str


class ActualResponse(BaseModel):
    record_id: int

    canteen_name: str
    prediction_date: date

    expected_portions: float
    actual_portions: int
    absolute_error: float

    actual_recorded_at: Optional[str] = None