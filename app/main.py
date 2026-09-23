from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import DailyRecord
from .schemas import (
    PredictionRequest,
    PredictionResponse,
    ActualSalesRequest
)
from .features import create_prediction_features
from .ml_model import predict


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Food Demand Forecasting API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Smart Food Demand Forecasting API",
        "status": "running"
    }
    
@app.post(
    "/predict",
    response_model=PredictionResponse
)

def predict_demand(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):

    historical_records = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.store == request.store,
            DailyRecord.actual_sales.isnot(None),
            DailyRecord.date < request.date
        )
        .order_by(DailyRecord.date)
        .all()
    )

    history = [
        {
            "date": record.date,
            "actual_sales": record.actual_sales
        }
        for record in historical_records
    ]

    try:

        features = create_prediction_features(
            current_date=request.date,
            store=request.store,

            is_state_holiday=request.is_state_holiday,
            is_school_holiday=request.is_school_holiday,
            is_special_day=request.is_special_day,

            temperature_max=request.temperature_max,
            temperature_min=request.temperature_min,
            temperature_mean=request.temperature_mean,

            sunshine_sum=request.sunshine_sum,
            precipitation_sum=request.precipitation_sum,

            historical_records=history
        )

        prediction = predict(features)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    record = DailyRecord(
        date=request.date,
        store=request.store,

        is_state_holiday=request.is_state_holiday,
        is_school_holiday=request.is_school_holiday,
        is_special_day=request.is_special_day,

        temperature_max=request.temperature_max,
        temperature_min=request.temperature_min,
        temperature_mean=request.temperature_mean,

        sunshine_sum=request.sunshine_sum,
        precipitation_sum=request.precipitation_sum,

        prediction=prediction,
        actual_sales=None
    )

    db.add(record)
    db.commit()

    return {
        "date": request.date,
        "store": request.store,
        "prediction": prediction
    }
    

@app.post("/actual")
def add_actual_sales(
    request: ActualSalesRequest,
    db: Session = Depends(get_db)
):

    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.date == request.date,
            DailyRecord.store == request.store
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Prediction record not found."
        )

    record.actual_sales = request.actual_sales

    db.commit()

    return {
        "message": "Actual sales recorded successfully.",
        "date": request.date,
        "store": request.store,
        "actual_sales": request.actual_sales,
        "prediction": record.prediction
    }
    
@app.get("/records")
def get_records(
    db: Session = Depends(get_db)
):

    records = (
        db.query(DailyRecord)
        .order_by(DailyRecord.date.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "date": r.date,
            "store": r.store,
            "prediction": r.prediction,
            "actual_sales": r.actual_sales
        }
        for r in records
    ]
    
