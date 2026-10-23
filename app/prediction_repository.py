from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from app.database import prediction_collection
from app.calibration import DemandCalibration


def utc_now():
    return datetime.now(timezone.utc)


def serialize_record(record):
    """Convert MongoDB values into JSON-friendly values."""

    if record is None:
        return None

    result = dict(record)
    result["id"] = str(result.pop("_id"))

    for key in ("created_at", "actual_recorded_at"):
        value = result.get(key)
        if value is not None:
            result[key] = value.isoformat()

    return result


def save_prediction(result: dict) -> dict:
    """Save or return the existing prediction for a canteen/date."""

    prediction_date = result["prediction_date"]
    store_id = result["store_id"]

    document = {
        "store_id": store_id,
        "canteen_name": result["canteen_name"],
        "prediction_date": prediction_date,

        "is_state_holiday": int(
            result["calendar"]["is_state_holiday"]
        ),
        "is_school_holiday": int(
            result["calendar"]["is_school_holiday"]
        ),
        "is_special_day": int(
            result["calendar"]["is_special_day"]
        ),

        "temperature_max": float(
            result["weather"]["temperature_max"]
        ),
        "temperature_min": float(
            result["weather"]["temperature_min"]
        ),
        "temperature_mean": float(
            result["weather"]["temperature_mean"]
        ),
        "sunshine_sum": float(
            result["weather"]["sunshine_sum"]
        ),
        "precipitation_sum": float(
            result["weather"]["precipitation_sum"]
        ),

        "sales_lag_1": float(
            result["historical_features"]["sales_lag_1"]
        ),
        "sales_lag_7": float(
            result["historical_features"]["sales_lag_7"]
        ),
        "sales_rolling_mean_7": float(
            result["historical_features"]["sales_rolling_mean_7"]
        ),

        "scaled_prediction": float(
            result["scaled_prediction"]
        ),
        "expected_portions": float(
            result["expected_portions"]
        ),
        "safety_buffer": int(result["safety_buffer"]),
        "recommended_portions": int(
            result["recommended_portions"]
        ),

        "actual_portions": None,
        "absolute_error": None,

        "model_version": result["model_version"],
        "calibration_version": result["calibration_version"],

        "created_at": utc_now(),
        "actual_recorded_at": None,
    }

    # Idempotent insert: return an existing record for this date
    # instead of creating a duplicate.
    try:
        prediction_collection.update_one(
            {
                "store_id": store_id,
                "prediction_date": prediction_date,
            },
            {"$setOnInsert": document},
            upsert=True,
        )
    except Exception:
        # The unique index protects against simultaneous duplicate
        # requests. Re-read below if another request inserted first.
        existing = prediction_collection.find_one(
            {
                "store_id": store_id,
                "prediction_date": prediction_date,
            }
        )
        if existing is None:
            raise

    record = prediction_collection.find_one(
        {
            "store_id": store_id,
            "prediction_date": prediction_date,
        }
    )

    return serialize_record(record)


def get_record(record_id: str) -> dict | None:
    if not ObjectId.is_valid(record_id):
        return None

    record = prediction_collection.find_one(
        {"_id": ObjectId(record_id)}
    )

    return serialize_record(record)


def save_actual(record_id: str, actual_portions: int) -> dict:
    """Record actual portions and retrain calibration when eligible."""

    if actual_portions < 0:
        raise ValueError("Actual portions cannot be negative.")

    if not ObjectId.is_valid(record_id):
        raise ValueError("Invalid prediction record ID.")

    existing = prediction_collection.find_one(
        {"_id": ObjectId(record_id)}
    )

    if existing is None:
        raise ValueError("Prediction record not found.")

    if existing.get("actual_portions") is not None:
        raise ValueError("Actual portions have already been recorded.")

    absolute_error = abs(
        float(existing["expected_portions"]) - actual_portions
    )

    # Conditional update prevents two requests from recording
    # actual portions for the same record at the same time.
    updated = prediction_collection.find_one_and_update(
        {
            "_id": ObjectId(record_id),
            "actual_portions": None,
        },
        {
            "$set": {
                "actual_portions": int(actual_portions),
                "absolute_error": float(absolute_error),
                "actual_recorded_at": utc_now(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )

    if updated is None:
        raise ValueError(
            "Actual portions have already been recorded."
        )

    store_id = updated["store_id"]

    completed = list(
        prediction_collection.find(
            {
                "store_id": store_id,
                "actual_portions": {"$ne": None},
                "scaled_prediction": {"$ne": None},
            }
        ).sort("prediction_date", 1)
    )

    if len(completed) >= DemandCalibration.MIN_OBSERVATIONS:
        calibration = DemandCalibration()

        calibration.fit_canteen(
            store_id=store_id,
            scaled_predictions=[
                float(r["scaled_prediction"]) for r in completed
            ],
            actual_portions=[
                float(r["actual_portions"]) for r in completed
            ],
        )

    return serialize_record(updated)


def get_all_records():
    records = prediction_collection.find().sort(
        "prediction_date", -1
    )
    return [serialize_record(record) for record in records]


def get_completed_records(store_id: str | None = None):
    query = {"actual_portions": {"$ne": None}}

    if store_id is not None:
        query["store_id"] = store_id

    records = prediction_collection.find(query).sort(
        "prediction_date", 1
    )

    return [serialize_record(record) for record in records]