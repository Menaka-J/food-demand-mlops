from datetime import date

from app.database import SessionLocal
from app.prediction_repository import (
    save_prediction,
    save_actual,
)
from app.prediction_service import (
    PredictionService,
)


print("=" * 70)
print("PREDICTION + ACTUAL DATABASE TEST")
print("=" * 70)


# ---------------------------------------------------------
# Generate prediction
# ---------------------------------------------------------

service = PredictionService()

result = service.predict(
    store_id="store_0",
    prediction_date=date.today(),
    is_state_holiday=False,
    is_school_holiday=False,
    is_special_day=False,
)


# ---------------------------------------------------------
# Save prediction
# ---------------------------------------------------------

db = SessionLocal()

try:

    record = save_prediction(
        db=db,
        result=result,
    )

    print()
    print("PREDICTION SAVED")
    print("-" * 70)

    print(f"Record ID          : {record.id}")
    print(f"Canteen            : {record.canteen_name}")
    print(f"Date               : {record.prediction_date}")
    print(
        f"Scaled prediction : "
        f"{record.scaled_prediction:.6f}"
    )
    print(
        f"Expected portions : "
        f"{record.expected_portions}"
    )
    print(
        f"Recommended       : "
        f"{record.recommended_portions}"
    )


    # -----------------------------------------------------
    # Simulate end-of-day actual
    # -----------------------------------------------------

    actual_value = 247

    record = save_actual(
        db=db,
        record_id=record.id,
        actual_portions=actual_value,
    )

    print()
    print("ACTUAL SAVED")
    print("-" * 70)

    print(
        f"Expected portions : "
        f"{record.expected_portions}"
    )

    print(
        f"Actual portions   : "
        f"{record.actual_portions}"
    )

    print(
        f"Absolute error    : "
        f"{record.absolute_error}"
    )

    print(
        f"Recorded at       : "
        f"{record.actual_recorded_at}"
    )


finally:
    db.close()


print()
print("=" * 70)
print("DATABASE OPERATION TEST COMPLETED")
print("=" * 70)