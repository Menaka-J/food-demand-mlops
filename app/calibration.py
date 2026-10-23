import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from app.database import calibration_collection


MIN_OBSERVATIONS = 5


class DemandCalibration:
    MIN_OBSERVATIONS = MIN_OBSERVATIONS

    def has_calibration(self, store_id: str) -> bool:
        item = calibration_collection.find_one(
            {"store_id": store_id}
        )

        return bool(
            item
            and item.get("method") == "linear_calibration"
            and item.get("observations", 0) >= MIN_OBSERVATIONS
        )

    def predict_portions(
        self,
        store_id: str,
        scaled_prediction: float,
        baseline_portions: int,
    ) -> int:
        item = calibration_collection.find_one(
            {"store_id": store_id}
        )

        if (
            item
            and item.get("method") == "linear_calibration"
            and item.get("observations", 0) >= MIN_OBSERVATIONS
        ):
            predicted = (
                float(item["intercept"])
                + float(item["coefficient"]) * scaled_prediction
            )
            return max(0, round(predicted))

        return round(baseline_portions)

    def fit_canteen(
        self,
        store_id: str,
        scaled_predictions,
        actual_portions,
    ) -> dict:
        count = min(
            len(scaled_predictions),
            len(actual_portions),
        )

        if count < MIN_OBSERVATIONS:
            return {
                "status": "insufficient_data",
                "store_id": store_id,
                "observations": count,
                "required_observations": MIN_OBSERVATIONS,
            }

        X = np.asarray(
            scaled_predictions[:count],
            dtype=float,
        ).reshape(-1, 1)

        y = np.asarray(
            actual_portions[:count],
            dtype=float,
        )

        model = LinearRegression()
        model.fit(X, y)

        predicted = model.predict(X)
        training_mae = float(mean_absolute_error(y, predicted))

        document = {
            "store_id": store_id,
            "method": "linear_calibration",
            "observations": count,
            "coefficient": float(model.coef_[0]),
            "intercept": float(model.intercept_),
            "training_mae": training_mae,
        }

        calibration_collection.update_one(
            {"store_id": store_id},
            {"$set": document},
            upsert=True,
        )

        return {
            "status": "calibrated",
            **document,
        }

    def get_status(
        self,
        store_id: str,
        completed_observations: int,
    ) -> dict:
        item = calibration_collection.find_one(
            {"store_id": store_id},
            {"_id": 0},
        )

        if not item:
            return {
                "store_id": store_id,
                "observations": completed_observations,
                "required_observations": MIN_OBSERVATIONS,
                "status": "not_calibrated",
                "method": "initial_baseline",
            }

        return {
            **item,
            "required_observations": MIN_OBSERVATIONS,
            "status": "calibrated",
        }

    def get_all(self) -> dict:
        documents = calibration_collection.find(
            {},
            {"_id": 0},
        )

        return {
            item["store_id"]: item
            for item in documents
        }