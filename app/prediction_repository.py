from datetime import datetime, date

from sqlalchemy.orm import Session

from app.models import PredictionRecord


def _parse_prediction_date(value) -> date:
    """
    Convert the prediction date into a Python date object.

    The prediction service returns dates as ISO strings
    because they are suitable for API/JSON responses.
    SQLAlchemy's Date column requires a Python date object.
    """

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    raise TypeError(
        "prediction_date must be a Python date "
        "or an ISO date string."
    )


def save_prediction(
    db: Session,
    result: dict,
) -> PredictionRecord:

    prediction_date = _parse_prediction_date(
        result["prediction_date"]
    )

    # -----------------------------------------------------
    # Prevent duplicate prediction for the same
    # canteen and prediction date.
    # -----------------------------------------------------

    existing = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.store_id
            == result["store_id"],

            PredictionRecord.prediction_date
            == prediction_date,
        )
        .first()
    )

    if existing is not None:
        return existing

    # -----------------------------------------------------
    # Create new prediction record
    # -----------------------------------------------------

    record = PredictionRecord(
        store_id=result["store_id"],

        canteen_name=result["canteen_name"],

        prediction_date=prediction_date,

        is_state_holiday=int(
            result["calendar"]["is_state_holiday"]
        ),

        is_school_holiday=int(
            result["calendar"]["is_school_holiday"]
        ),

        is_special_day=int(
            result["calendar"]["is_special_day"]
        ),

        temperature_max=result["weather"][
            "temperature_max"
        ],

        temperature_min=result["weather"][
            "temperature_min"
        ],

        temperature_mean=result["weather"][
            "temperature_mean"
        ],

        sunshine_sum=result["weather"][
            "sunshine_sum"
        ],

        precipitation_sum=result["weather"][
            "precipitation_sum"
        ],

        sales_lag_1=result["historical_features"][
            "sales_lag_1"
        ],

        sales_lag_7=result["historical_features"][
            "sales_lag_7"
        ],

        sales_rolling_mean_7=result[
            "historical_features"
        ][
            "sales_rolling_mean_7"
        ],

        scaled_prediction=result[
            "scaled_prediction"
        ],

        expected_portions=result[
            "expected_portions"
        ],

        safety_buffer=result[
            "safety_buffer"
        ],

        recommended_portions=result[
            "recommended_portions"
        ],

        model_version=result[
            "model_version"
        ],

        calibration_version=result[
            "calibration_version"
        ],

        created_at=datetime.utcnow(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def save_actual(
    db: Session,
    record_id: int,
    actual_portions: int,
) -> PredictionRecord:

    if actual_portions < 0:
        raise ValueError(
            "Actual portions cannot be negative."
        )

    record = db.get(
        PredictionRecord,
        record_id,
    )

    if record is None:
        raise ValueError(
            f"Prediction record {record_id} "
            "was not found."
        )

    if record.actual_portions is not None:
        raise ValueError(
            f"Actual portions have already been "
            f"recorded for prediction record "
            f"{record_id}."
        )

    record.actual_portions = actual_portions

    record.absolute_error = abs(
        record.expected_portions
        - actual_portions
    )

    record.actual_recorded_at = (
        datetime.utcnow()
    )

    db.commit()
    db.refresh(record)

    return record