from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import PredictionRecord
from app.prediction_repository import (
    save_actual,
    save_prediction,
)
from app.prediction_service import PredictionService
from app.schemas import (
    ActualRequest,
    ActualResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.config import get_all_canteens


app = FastAPI(
    title="Smart Food Demand Forecasting API",
    description=(
        "API for food-demand forecasting, "
        "portion planning and MLOps monitoring."
    ),
    version="1.0.0",
)


prediction_service = PredictionService()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "application": (
            "Smart Food Demand Forecasting "
            "and Waste Reduction System"
        ),
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/canteens")
def get_canteens():
    return [
        {
            "store_id": canteen.store_id,
            "name": canteen.name,
            "city": canteen.city,
            "state": canteen.state,
        }
        for canteen in get_all_canteens()
    ]


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def create_prediction(
    request: PredictionRequest,
    db: Session = Depends(get_db),
):

    try:

        # -------------------------------------------------
        # Generate prediction
        # -------------------------------------------------

        result = prediction_service.predict(
            store_id=request.store_id,
            prediction_date=request.prediction_date,
            is_state_holiday=request.is_state_holiday,
            is_school_holiday=request.is_school_holiday,
            is_special_day=request.is_special_day,
        )

        # -------------------------------------------------
        # Save prediction
        # -------------------------------------------------

        record = save_prediction(
            db=db,
            result=result,
        )

        return {
            "record_id": record.id,

            "store_id": record.store_id,
            "canteen_name": record.canteen_name,
            "city": result["city"],
            "state": result["state"],

            "prediction_date": record.prediction_date,

            "is_state_holiday": bool(
                record.is_state_holiday
            ),

            "is_school_holiday": bool(
                record.is_school_holiday
            ),

            "is_special_day": bool(
                record.is_special_day
            ),

            "temperature_max": (
                record.temperature_max
            ),

            "temperature_min": (
                record.temperature_min
            ),

            "temperature_mean": (
                record.temperature_mean
            ),

            "sunshine_sum": (
                record.sunshine_sum
            ),

            "precipitation_sum": (
                record.precipitation_sum
            ),

            "scaled_prediction": (
                record.scaled_prediction
            ),

            "expected_portions": (
                record.expected_portions
            ),

            "safety_buffer": (
                record.safety_buffer
            ),

            "recommended_portions": (
                record.recommended_portions
            ),

            "model_version": (
                record.model_version
            ),

            "calibration_version": (
                record.calibration_version
            ),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        )


@app.post(
    "/actual/{record_id}",
    response_model=ActualResponse,
)
def record_actual(
    record_id: int,
    request: ActualRequest,
    db: Session = Depends(get_db),
):

    try:

        record = save_actual(
            db=db,
            record_id=record_id,
            actual_portions=request.actual_portions,
        )

        return {
            "record_id": record.id,

            "canteen_name": (
                record.canteen_name
            ),

            "prediction_date": (
                record.prediction_date
            ),

            "expected_portions": (
                record.expected_portions
            ),

            "actual_portions": (
                record.actual_portions
            ),

            "absolute_error": (
                record.absolute_error
            ),

            "actual_recorded_at": (
                record.actual_recorded_at.isoformat()
                if record.actual_recorded_at
                else None
            ),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Saving actual failed: {str(exc)}",
        )


@app.get("/records")
def get_records(
    db: Session = Depends(get_db),
):

    records = (
        db.query(PredictionRecord)
        .order_by(
            PredictionRecord.prediction_date.desc()
        )
        .all()
    )

    return [
        {
            "id": record.id,
            "store_id": record.store_id,
            "canteen_name": record.canteen_name,
            "prediction_date": (
                record.prediction_date
            ),

            "scaled_prediction": (
                record.scaled_prediction
            ),

            "expected_portions": (
                record.expected_portions
            ),

            "recommended_portions": (
                record.recommended_portions
            ),

            "actual_portions": (
                record.actual_portions
            ),

            "absolute_error": (
                record.absolute_error
            ),

            "model_version": (
                record.model_version
            ),

            "calibration_version": (
                record.calibration_version
            ),
        }
        for record in records
    ]


@app.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
):

    records = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.actual_portions.isnot(None)
        )
        .all()
    )

    if not records:
        return {
            "records_with_actuals": 0,
            "mae": None,
            "rmse": None,
            "mean_error": None,
            "message": (
                "No completed operational "
                "records available yet."
            ),
        }

    errors = [
        record.expected_portions
        - record.actual_portions
        for record in records
    ]

    absolute_errors = [
        abs(error)
        for error in errors
    ]

    squared_errors = [
        error ** 2
        for error in errors
    ]

    mae = sum(absolute_errors) / len(
        absolute_errors
    )

    rmse = (
        sum(squared_errors) / len(
            squared_errors
        )
    ) ** 0.5

    mean_error = sum(errors) / len(errors)

    return {
        "records_with_actuals": len(records),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mean_error": round(mean_error, 4),
    }