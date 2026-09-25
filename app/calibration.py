import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


CALIBRATION_PATH = Path(
    "models/operational_calibration.json"
)

MIN_OBSERVATIONS = 5


class DemandCalibration:

    def __init__(
        self,
        path=CALIBRATION_PATH
    ):

        self.path = Path(path)

        self.data = self._load()


    # =====================================================
    # LOAD CALIBRATION
    # =====================================================

    def _load(self):

        if not self.path.exists():

            return {
                "version": 1,
                "canteens": {}
            }

        try:

            with open(
                self.path,
                "r"
            ) as file:

                data = json.load(file)

        except (
            json.JSONDecodeError,
            OSError
        ):

            return {
                "version": 1,
                "canteens": {}
            }


        # -------------------------------------------------
        # Ensure correct structure
        # -------------------------------------------------

        if "canteens" not in data:

            return {
                "version": 1,
                "canteens": {}
            }


        return data


    # =====================================================
    # SAVE CALIBRATION
    # =====================================================

    def _save(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.path,
            "w"
        ) as file:

            json.dump(
                self.data,
                file,
                indent=4
            )


    # =====================================================
    # CHECK WHETHER A CANTEEN HAS CALIBRATION
    # =====================================================

    def has_calibration(
        self,
        store_id: str
    ) -> bool:

        canteen = self.data[
            "canteens"
        ].get(store_id)

        if canteen is None:
            return False

        return (
            canteen.get("method")
            == "linear_calibration"
            and
            canteen.get("observations", 0)
            >= MIN_OBSERVATIONS
        )


    # =====================================================
    # PREDICT PORTIONS
    # =====================================================

    def predict_portions(
        self,
        store_id: str,
        scaled_prediction: float,
        baseline_portions: int
    ) -> int:

        # -------------------------------------------------
        # Check for learned calibration
        # -------------------------------------------------

        if self.has_calibration(store_id):

            canteen = self.data[
                "canteens"
            ][store_id]

            coefficient = float(
                canteen["coefficient"]
            )

            intercept = float(
                canteen["intercept"]
            )

            predicted_portions = (
                intercept
                + coefficient * scaled_prediction
            )

            return max(
                0,
                round(predicted_portions)
            )


        # -------------------------------------------------
        # No learned calibration yet
        # -------------------------------------------------

        return round(
            baseline_portions
        )


    # =====================================================
    # TRAIN CALIBRATION FOR ONE CANTEEN
    # =====================================================

    def fit_canteen(
        self,
        store_id: str,
        scaled_predictions,
        actual_portions
    ) -> dict:

        observation_count = min(
            len(scaled_predictions),
            len(actual_portions)
        )


        # -------------------------------------------------
        # Minimum data check
        # -------------------------------------------------

        if observation_count < MIN_OBSERVATIONS:

            return {
                "status": "insufficient_data",
                "store_id": store_id,
                "observations": observation_count,
                "required_observations": MIN_OBSERVATIONS,
                "message": (
                    f"Need at least "
                    f"{MIN_OBSERVATIONS} "
                    f"completed observations. "
                    f"Currently have "
                    f"{observation_count}."
                )
            }


        # -------------------------------------------------
        # Convert data to arrays
        # -------------------------------------------------

        X = np.array(
            scaled_predictions,
            dtype=float
        ).reshape(-1, 1)

        y = np.array(
            actual_portions,
            dtype=float
        )


        # -------------------------------------------------
        # Train linear calibration
        # -------------------------------------------------

        model = LinearRegression()

        model.fit(
            X,
            y
        )


        # -------------------------------------------------
        # Calculate training error
        # -------------------------------------------------

        calibrated_predictions = model.predict(X)

        training_mae = mean_absolute_error(
            y,
            calibrated_predictions
        )


        # -------------------------------------------------
        # Extract parameters
        # -------------------------------------------------

        coefficient = float(
            model.coef_[0]
        )

        intercept = float(
            model.intercept_
        )


        # -------------------------------------------------
        # Save calibration
        # -------------------------------------------------

        self.data["canteens"][store_id] = {

            "method": "linear_calibration",

            "observations": observation_count,

            "coefficient": coefficient,

            "intercept": intercept,

            "training_mae": float(
                training_mae
            )
        }


        self._save()


        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return {

            "status": "calibrated",

            "store_id": store_id,

            "observations": observation_count,

            "coefficient": coefficient,

            "intercept": intercept,

            "training_mae": float(
                training_mae
            )
        }


    # =====================================================
    # GET ONE CANTEEN CALIBRATION STATUS
    # =====================================================

    def get_status(
        self,
        store_id: str,
        completed_observations: int
    ) -> dict:

        canteen = self.data[
            "canteens"
        ].get(store_id)


        # -------------------------------------------------
        # No calibration
        # -------------------------------------------------

        if canteen is None:

            return {

                "store_id": store_id,

                "observations": (
                    completed_observations
                ),

                "required_observations": (
                    MIN_OBSERVATIONS
                ),

                "status": "not_calibrated",

                "method": "initial_baseline"
            }


        # -------------------------------------------------
        # Existing calibration
        # -------------------------------------------------

        return {

            "store_id": store_id,

            "observations": canteen.get(
                "observations",
                completed_observations
            ),

            "required_observations": (
                MIN_OBSERVATIONS
            ),

            "status": "calibrated",

            "method": canteen.get(
                "method"
            ),

            "coefficient": canteen.get(
                "coefficient"
            ),

            "intercept": canteen.get(
                "intercept"
            ),

            "training_mae": canteen.get(
                "training_mae"
            )
        }


    # =====================================================
    # GET ALL CALIBRATIONS
    # =====================================================

    def get_all(self) -> dict:

        return self.data.get(
            "canteens",
            {}
        )