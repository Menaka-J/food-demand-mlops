import pandas as pd

from app.calibration import DemandCalibration


calibration = DemandCalibration()


print("=" * 70)
print("CALIBRATION TEST")
print("=" * 70)


# ---------------------------------------------------------
# 1. Initial prediction
# ---------------------------------------------------------

initial = calibration.predict_portions(
    store_id="store_0",
    scaled_prediction=0.42,
    baseline_portions=250,
)

print()
print("INITIAL CALIBRATION")
print(f"Scaled prediction : 0.42")
print(f"Expected portions : {initial}")


# ---------------------------------------------------------
# 2. Simulated operational observations
# ---------------------------------------------------------

records = pd.DataFrame({
    "scaled_prediction": [
        -0.40,
        -0.10,
        0.10,
        0.30,
        0.50,
        0.70,
        1.00,
    ],
    "actual_portions": [
        210,
        225,
        235,
        248,
        260,
        275,
        300,
    ],
})


print()
print("FITTING CALIBRATION")

result = calibration.fit_store_calibration(
    store_id="store_0",
    records=records,
)

print(f"Method       : {result['method']}")
print(f"Observations : {result['observations']}")
print(f"Coefficient  : {result['coefficient']:.4f}")
print(f"Intercept    : {result['intercept']:.4f}")
print(f"Training MAE : {result['training_mae']:.4f}")


# ---------------------------------------------------------
# 3. Prediction using learned calibration
# ---------------------------------------------------------

predicted = calibration.predict_portions(
    store_id="store_0",
    scaled_prediction=0.42,
    baseline_portions=250,
)

print()
print("LEARNED CALIBRATION PREDICTION")
print(f"Scaled prediction : 0.42")
print(f"Expected portions : {predicted:.2f}")

print()
print("=" * 70)
print("CALIBRATION TEST COMPLETED")
print("=" * 70)