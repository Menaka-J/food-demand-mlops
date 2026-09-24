from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CALIBRATION_DIR = PROJECT_ROOT / "models"
CALIBRATION_DIR.mkdir(exist_ok=True)

CALIBRATION_PATH = (
    CALIBRATION_DIR / "operational_calibration.json"
)


class DemandCalibration:

    def __init__(self):
        self.calibrations = {}

        if CALIBRATION_PATH.exists():
            with open(
                CALIBRATION_PATH,
                "r",
                encoding="utf-8",
            ) as f:
                self.calibrations = json.load(f)

    def save(self):
        with open(
            CALIBRATION_PATH,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.calibrations,
                f,
                indent=4,
            )

    def has_calibration(self, store_id: str) -> bool:
        return store_id in self.calibrations

    def get_initial_prediction(
        self,
        store_id: str,
        scaled_prediction: float,
        baseline_portions: int,
    ) -> float:
        """
        Initial deployment calibration.

        Before operational data exists, use the configured
        canteen baseline as the starting operational estimate.

        The scaled model output is still stored separately.
        """

        return float(baseline_portions)

    def predict_portions(
        self,
        store_id: str,
        scaled_prediction: float,
        baseline_portions: int,
    ) -> float:

        if store_id not in self.calibrations:
            return self.get_initial_prediction(
                store_id=store_id,
                scaled_prediction=scaled_prediction,
                baseline_portions=baseline_portions,
            )

        calibration = self.calibrations[store_id]

        intercept = calibration["intercept"]
        coefficient = calibration["coefficient"]

        predicted = (
            intercept
            + coefficient * scaled_prediction
        )

        return max(0.0, float(predicted))

    def fit_store_calibration(
        self,
        store_id: str,
        records: pd.DataFrame,
    ) -> dict:
        """
        Learn the relationship:

            actual portions
                     ↑
                     |
            scaled model prediction

        for one canteen.
        """

        required_columns = {
            "scaled_prediction",
            "actual_portions",
        }

        missing = required_columns - set(records.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )

        data = records.dropna(
            subset=[
                "scaled_prediction",
                "actual_portions",
            ]
        ).copy()

        if len(data) < 5:
            raise ValueError(
                "At least 5 operational observations "
                "are required to fit calibration."
            )

        X = data[
            ["scaled_prediction"]
        ]

        y = data["actual_portions"]

        model = LinearRegression()
        model.fit(X, y)

        coefficient = float(
            model.coef_[0]
        )

        intercept = float(
            model.intercept_
        )

        predictions = model.predict(X)

        mae = float(
            np.mean(
                np.abs(
                    predictions - y
                )
            )
        )

        self.calibrations[store_id] = {
            "method": "linear_calibration",
            "observations": int(len(data)),
            "coefficient": coefficient,
            "intercept": intercept,
            "training_mae": mae,
        }

        self.save()

        return self.calibrations[store_id]