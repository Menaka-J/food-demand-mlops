from datetime import date
from typing import Optional

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    date: date
    store: str

    is_state_holiday: str
    is_school_holiday: str
    is_special_day: str

    temperature_max: float
    temperature_min: float
    temperature_mean: float

    sunshine_sum: float
    precipitation_sum: float


class PredictionResponse(BaseModel):
    date: date
    store: str
    prediction: float


class ActualSalesRequest(BaseModel):
    date: date
    store: str
    actual_sales: float