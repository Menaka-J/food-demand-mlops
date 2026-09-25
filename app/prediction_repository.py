from datetime import datetime

from sqlalchemy.orm import Session

from app.calibration import DemandCalibration
from app.models import PredictionRecord


def save_prediction(db: Session, result: dict) -> PredictionRecord:
    """
    Save a prediction.

    Prevent duplicate predictions for the same canteen and date.
    """

    prediction_date = datetime.strptime(
        result["prediction_date"], "%Y-%m-%d"
    ).date()

    existing = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.store_id == result["store_id"],
            PredictionRecord.prediction_date == prediction_date,
        )
        .first()
    )

    if existing is not None:
        return existing

    record = PredictionRecord(
        store_id=result["store_id"],
        canteen_name=result["canteen_name"],
        prediction_date=prediction_date,

        is_state_holiday=result["calendar"]["is_state_holiday"],
        is_school_holiday=result["calendar"]["is_school_holiday"],
        is_special_day=result["calendar"]["is_special_day"],

        temperature_max=result["weather"]["temperature_max"],
        temperature_min=result["weather"]["temperature_min"],
        temperature_mean=result["weather"]["temperature_mean"],
        sunshine_sum=result["weather"]["sunshine_sum"],
        precipitation_sum=result["weather"]["precipitation_sum"],

        sales_lag_1=result["historical_features"]["sales_lag_1"],
        sales_lag_7=result["historical_features"]["sales_lag_7"],
        sales_rolling_mean_7=result["historical_features"]["sales_rolling_mean_7"],

        scaled_prediction=result["scaled_prediction"],
        expected_portions=result["expected_portions"],
        safety_buffer=result["safety_buffer"],
        recommended_portions=result["recommended_portions"],

        model_version=result["model_version"],
        calibration_version=result["calibration_version"],

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
    """
    Save the actual portions consumed/sold for a prediction.

    Once a canteen reaches the minimum number of genuine completed
    observations, automatically train its operational calibration.
    """

    if actual_portions < 0:
        raise ValueError("Actual portions cannot be negative.")

    record = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.id == record_id)
        .first()
    )

    if record is None:
        raise ValueError("Prediction record not found.")

    if record.actual_portions is not None:
        raise ValueError("Actual portions have already been recorded.")

    record.actual_portions = actual_portions

    # Error = expected - actual
    record.absolute_error = abs(
        record.expected_portions - actual_portions
    )

    record.actual_recorded_at = datetime.utcnow()

    db.commit()
    db.refresh(record)

    # ---------------------------------------------------------
    # AUTOMATIC OPERATIONAL CALIBRATION
    # ---------------------------------------------------------
    #
    # Calibration is trained independently for each canteen.
    # It requires at least 5 genuine completed observations.
    #
    # We only use records that have:
    #   1. a scaled prediction
    #   2. an actual operational portion value
    #
    # We DO NOT modify the base MLflow model.
    # ---------------------------------------------------------

    completed_records = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.store_id == record.store_id,
            PredictionRecord.actual_portions.isnot(None),
            PredictionRecord.scaled_prediction.isnot(None),
        )
        .order_by(PredictionRecord.prediction_date.asc())
        .all()
    )

    if len(completed_records) >= DemandCalibration.MIN_OBSERVATIONS:

        scaled_predictions = [
            float(r.scaled_prediction)
            for r in completed_records
        ]

        actual_portions_list = [
            float(r.actual_portions)
            for r in completed_records
        ]

        calibration = DemandCalibration()

        calibration.fit_canteen(
            store_id=record.store_id,
            scaled_predictions=scaled_predictions,
            actual_portions=actual_portions_list,
        )

    return record


def get_completed_records(
    db: Session,
    store_id: str | None = None,
):
    """
    Return prediction records for which actual portions
    have already been recorded.
    """

    query = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.actual_portions.isnot(None))
    )

    if store_id is not None:
        query = query.filter(
            PredictionRecord.store_id == store_id
        )

    return (
        query
        .order_by(PredictionRecord.prediction_date.asc())
        .all()
    )