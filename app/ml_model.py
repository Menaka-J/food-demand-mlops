
import os

import mlflow
import mlflow.sklearn
import pandas as pd


MODEL_URI = os.getenv(
    "MODEL_URI",
    "models:/SmartFoodDemandModel/1",
)

TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    (
        "sqlite:///C:/Users/Menaka/"
        "Videos/smart-food-demand-mlops/mlflow.db"
    ),
)


class DemandModel:

    def __init__(self):
        mlflow.set_tracking_uri(TRACKING_URI)

        print("Loading MLflow model...")
        print(f"Tracking URI: {TRACKING_URI}")
        print(f"Model URI: {MODEL_URI}")

        self.model = mlflow.sklearn.load_model(MODEL_URI)

        print("MLflow model loaded successfully.")

    def predict(self, features: dict) -> float:
        feature_order = [
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

        missing_features = [
            column
            for column in feature_order
            if column not in features
        ]

        if missing_features:
            raise ValueError(
                "Missing model features: "
                + ", ".join(missing_features)
            )

        input_data = pd.DataFrame(
            [
                {
                    column: features[column]
                    for column in feature_order
                }
            ]
        )

        prediction = self.model.predict(input_data)[0]

        return float(prediction)
