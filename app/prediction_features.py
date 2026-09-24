from datetime import date

from app.config import get_canteen
from app.historical_features import (
    HistoricalFeatureService,
)
from app.weather import get_weather


class PredictionFeatureBuilder:

    def __init__(self):
        self.history = HistoricalFeatureService()

    def build(
        self,
        store_id: str,
        prediction_date: date,
        is_state_holiday: bool,
        is_school_holiday: bool,
        is_special_day: bool,
    ) -> dict:

        canteen = get_canteen(store_id)

        # -------------------------------------------------
        # 1. Automatically retrieve weather
        # -------------------------------------------------

        weather = get_weather(
            latitude=canteen.latitude,
            longitude=canteen.longitude,
            target_date=prediction_date,
        )

        # -------------------------------------------------
        # 2. Historical scaled-sales features
        # -------------------------------------------------

        historical = (
            self.history.get_latest_features(
                store_id
            )
        )

        # -------------------------------------------------
        # 3. Calendar features
        # -------------------------------------------------

        year = prediction_date.year
        month = prediction_date.month
        day = prediction_date.day

        day_of_week = prediction_date.weekday()

        week_of_year = (
            prediction_date.isocalendar().week
        )

        quarter = (
            (month - 1) // 3 + 1
        )

        is_weekend = (
            1 if day_of_week >= 5 else 0
        )

        # -------------------------------------------------
        # 4. Build model feature dictionary
        # -------------------------------------------------

        features = {
            "store": store_id,

            "is_state_holiday": int(
                is_state_holiday
            ),

            "is_school_holiday": int(
                is_school_holiday
            ),

            "is_special_day": int(
                is_special_day
            ),

            "temperature_max": weather[
                "temperature_max"
            ],

            "temperature_min": weather[
                "temperature_min"
            ],

            "temperature_mean": weather[
                "temperature_mean"
            ],

            "sunshine_sum": weather[
                "sunshine_sum"
            ],

            "precipitation_sum": weather[
                "precipitation_sum"
            ],

            "year": year,
            "month": month,
            "day": day,
            "day_of_week": day_of_week,
            "week_of_year": week_of_year,
            "quarter": quarter,
            "is_weekend": is_weekend,

            "sales_lag_1": historical[
                "sales_lag_1"
            ],

            "sales_lag_7": historical[
                "sales_lag_7"
            ],

            "sales_rolling_mean_7": historical[
                "sales_rolling_mean_7"
            ],
        }

        return {
            "features": features,
            "weather": weather,
            "historical": historical,
            "canteen": canteen,
        }