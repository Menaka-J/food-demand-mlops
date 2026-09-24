import mlflow
import mlflow.sklearn
import pandas as pd


MODEL_URI = "models:/SmartFoodDemandModel/1"

TRACKING_URI = (
    "sqlite:///C:/Users/Menaka/"
    "Videos/smart-food-demand-mlops/mlflow.db"
)


class DemandModel:

    def __init__(self):
        mlflow.set_tracking_uri(TRACKING_URI)

        print("Loading MLflow model...")
        print(f"Model URI: {MODEL_URI}")

        self.model = mlflow.sklearn.load_model(
            MODEL_URI
        )

        print("MLflow model loaded successfully.")

    def predict(self, features: dict) -> float:
        """
        Generate the original model's scaled demand prediction.

        The saved sklearn pipeline expects a pandas DataFrame
        because its preprocessing pipeline selects columns
        by their names.
        """

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

        # Make sure every expected feature exists.
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

        # IMPORTANT:
        # The trained sklearn pipeline expects a DataFrame
        # with the original feature names.
        input_data = pd.DataFrame(
            [
                {
                    column: features[column]
                    for column in feature_order
                }
            ]
        )

        prediction = self.model.predict(
            input_data
        )[0]

        return float(prediction)