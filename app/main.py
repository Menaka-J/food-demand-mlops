from fastapi import FastAPI, HTTPException

from app.calibration import DemandCalibration
from app.config import get_all_canteens, get_canteen
from app.database import initialize_database, prediction_collection
from app.prediction_repository import (
    get_all_records,
    get_completed_records,
    get_record,
    save_actual,
    save_prediction,
)
from app.prediction_service import PredictionService
from app.schemas import (
    ActualRequest,
    PredictionRequest,
)


app = FastAPI(
    title="Smart Food Demand Forecasting API",
    description=(
        "API for food-demand forecasting, portion planning "
        "and MLOps monitoring."
    ),
    version="1.0.0",
)

prediction_service = PredictionService()
calibration_service = DemandCalibration()


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def root():
    return {
        "application": (
            "Smart Food Demand Forecasting and Waste Reduction System"
        ),
        "status": "running",
        "database": "MongoDB Atlas",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    try:
        from app.database import client
        client.admin.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {exc}",
        )


@app.get("/canteens")
def list_canteens():
    return [
        {
            "store_id": canteen.store_id,
            "name": canteen.name,
            "city": canteen.city,
            "state": canteen.state,
        }
        for canteen in get_all_canteens()
    ]


@app.post("/predict")
def create_prediction(request: PredictionRequest):
    try:
        result = prediction_service.predict(
            store_id=request.store_id,
            prediction_date=request.prediction_date,
            is_state_holiday=request.is_state_holiday,
            is_school_holiday=request.is_school_holiday,
            is_special_day=request.is_special_day,
        )

        record = save_prediction(result)

        return {
            "record_id": record["id"],
            "store_id": record["store_id"],
            "canteen_name": record["canteen_name"],
            "city": result["city"],
            "state": result["state"],
            "prediction_date": record["prediction_date"],
            "is_state_holiday": bool(record["is_state_holiday"]),
            "is_school_holiday": bool(record["is_school_holiday"]),
            "is_special_day": bool(record["is_special_day"]),
            "temperature_max": record["temperature_max"],
            "temperature_min": record["temperature_min"],
            "temperature_mean": record["temperature_mean"],
            "sunshine_sum": record["sunshine_sum"],
            "precipitation_sum": record["precipitation_sum"],
            "scaled_prediction": record["scaled_prediction"],
            "expected_portions": record["expected_portions"],
            "safety_buffer": record["safety_buffer"],
            "recommended_portions": record["recommended_portions"],
            "model_version": record["model_version"],
            "calibration_version": record["calibration_version"],
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        )


@app.post("/actual/{record_id}")
def record_actual(record_id: str, request: ActualRequest):
    try:
        record = save_actual(
            record_id=record_id,
            actual_portions=request.actual_portions,
        )

        return {
            "record_id": record["id"],
            "canteen_name": record["canteen_name"],
            "prediction_date": record["prediction_date"],
            "expected_portions": record["expected_portions"],
            "actual_portions": record["actual_portions"],
            "absolute_error": record["absolute_error"],
            "actual_recorded_at": record.get("actual_recorded_at"),
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Saving actual failed: {exc}",
        )


@app.get("/records")
def list_records():
    return [
        {
            "id": record["id"],
            "store_id": record["store_id"],
            "canteen_name": record["canteen_name"],
            "prediction_date": record["prediction_date"],
            "scaled_prediction": record["scaled_prediction"],
            "expected_portions": record["expected_portions"],
            "recommended_portions": record["recommended_portions"],
            "actual_portions": record["actual_portions"],
            "absolute_error": record["absolute_error"],
            "model_version": record["model_version"],
            "calibration_version": record["calibration_version"],
        }
        for record in get_all_records()
    ]


@app.get("/metrics")
def get_metrics():
    records = get_completed_records()

    if not records:
        return {
            "records_with_actuals": 0,
            "mae": None,
            "rmse": None,
            "mean_error": None,
            "message": "No completed operational records available yet.",
        }

    errors = [
        float(r["expected_portions"]) - float(r["actual_portions"])
        for r in records
    ]

    mae = sum(abs(error) for error in errors) / len(errors)
    rmse = (sum(error ** 2 for error in errors) / len(errors)) ** 0.5
    mean_error = sum(errors) / len(errors)

    return {
        "records_with_actuals": len(records),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mean_error": round(mean_error, 4),
    }


@app.post("/calibration/{store_id}/train")
def train_calibration(store_id: str):
    try:
        get_canteen(store_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    records = get_completed_records(store_id)

    valid_records = [
        record for record in records
        if record.get("scaled_prediction") is not None
    ]

    if len(valid_records) < DemandCalibration.MIN_OBSERVATIONS:
        return {
            "status": "insufficient_data",
            "store_id": store_id,
            "observations": len(valid_records),
            "required_observations": DemandCalibration.MIN_OBSERVATIONS,
            "message": (
                "Need at least 5 completed observations. "
                f"Currently have {len(valid_records)}."
            ),
        }

    return calibration_service.fit_canteen(
        store_id=store_id,
        scaled_predictions=[
            record["scaled_prediction"] for record in valid_records
        ],
        actual_portions=[
            record["actual_portions"] for record in valid_records
        ],
    )


@app.get("/calibration/{store_id}")
def get_calibration_status(store_id: str):
    try:
        get_canteen(store_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    completed_count = len(get_completed_records(store_id))

    return calibration_service.get_status(
        store_id=store_id,
        completed_observations=completed_count,
    )


@app.get("/calibration")
def get_all_calibrations():
    return calibration_service.get_all()