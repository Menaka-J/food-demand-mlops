
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "candidate_model.joblib"
)

FEATURE_ORDER = [
    "store",
    "is_state_holiday",
    "is_school_holiday",
    "is_special_day",
    "temperature_max",
    "temperature_min",
    "temperature_mean",
    "sunshine_sum",
    "precipitation_sum",
    "year",
    "month",
    "day",
    "day_of_week",
    "week_of_year",
    "quarter",
    "is_weekend",
    "sales_lag_1",
    "sales_lag_7",
    "sales_rolling_mean_7",
]


class DemandModel:
    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found: {MODEL_PATH}"
            )

        self.model = joblib.load(MODEL_PATH)

    def predict(self, features: dict) -> float:
        missing = [
            name for name in FEATURE_ORDER
            if name not in features
        ]

        if missing:
            raise ValueError(
                f"Missing model features: {missing}"
            )

        frame = pd.DataFrame(
            [[features[name] for name in FEATURE_ORDER]],
            columns=FEATURE_ORDER,
        )

        prediction = self.model.predict(frame)
        return float(prediction[0])
