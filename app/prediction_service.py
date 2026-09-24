from datetime import date

from app.calibration import DemandCalibration
from app.config import get_canteen
from app.ml_model import DemandModel
from app.prediction_features import (
    PredictionFeatureBuilder,
)


class PredictionService:

    def __init__(self):
        self.model = DemandModel()
        self.feature_builder = (
            PredictionFeatureBuilder()
        )
        self.calibration = DemandCalibration()

    def predict(
        self,
        store_id: str,
        prediction_date: date,
        is_state_holiday: bool = False,
        is_school_holiday: bool = False,
        is_special_day: bool = False,
    ) -> dict:

        canteen = get_canteen(store_id)

        # -------------------------------------------------
        # Build all model features
        # -------------------------------------------------

        feature_data = (
            self.feature_builder.build(
                store_id=store_id,
                prediction_date=prediction_date,
                is_state_holiday=is_state_holiday,
                is_school_holiday=is_school_holiday,
                is_special_day=is_special_day,
            )
        )

        features = feature_data["features"]

        # -------------------------------------------------
        # Generate original ML prediction
        # -------------------------------------------------

        scaled_prediction = self.model.predict(
            features
        )

        # -------------------------------------------------
        # Convert scaled demand to portions
        # -------------------------------------------------

        expected_portions = (
            self.calibration.predict_portions(
                store_id=store_id,
                scaled_prediction=scaled_prediction,
                baseline_portions=(
                    canteen.initial_baseline_portions
                ),
            )
        )

        # -------------------------------------------------
        # Safety buffer
        # -------------------------------------------------

        safety_buffer = round(
            expected_portions
            * canteen.safety_buffer_percent
            / 100
        )

        recommended_portions = round(
            expected_portions
            + safety_buffer
        )

        return {
            "store_id": store_id,
            "canteen_name": canteen.name,
            "city": canteen.city,
            "state": canteen.state,

            "prediction_date": (
                prediction_date.isoformat()
            ),

            "calendar": {
                "is_state_holiday": (
                    is_state_holiday
                ),
                "is_school_holiday": (
                    is_school_holiday
                ),
                "is_special_day": (
                    is_special_day
                ),
            },

            "weather": feature_data[
                "weather"
            ],

            "historical_features": feature_data[
                "historical"
            ],

            "scaled_prediction": (
                scaled_prediction
            ),

            "expected_portions": (
                round(expected_portions)
            ),

            "safety_buffer": safety_buffer,

            "recommended_portions": (
                recommended_portions
            ),

            "model_version": "SmartFoodDemandModel/1",

            "calibration_version": (
                "initial_baseline"
                if not self.calibration.has_calibration(
                    store_id
                )
                else "learned_linear_calibration"
            ),
        }