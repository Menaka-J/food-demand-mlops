from datetime import date

from app.prediction_service import (
    PredictionService,
)


print("=" * 70)
print("END-TO-END PREDICTION TEST")
print("=" * 70)


service = PredictionService()


result = service.predict(
    store_id="store_0",
    prediction_date=date.today(),
    is_state_holiday=False,
    is_school_holiday=False,
    is_special_day=False,
)


print()
print("CANTEEN")
print("-" * 70)
print(f"Name     : {result['canteen_name']}")
print(f"Location : {result['city']}, {result['state']}")


print()
print("DATE")
print("-" * 70)
print(f"Date     : {result['prediction_date']}")


print()
print("CALENDAR")
print("-" * 70)
print(
    f"State Holiday  : "
    f"{result['calendar']['is_state_holiday']}"
)
print(
    f"School Holiday : "
    f"{result['calendar']['is_school_holiday']}"
)
print(
    f"Special Day    : "
    f"{result['calendar']['is_special_day']}"
)


print()
print("WEATHER")
print("-" * 70)

weather = result["weather"]

print(
    f"Maximum temperature : "
    f"{weather['temperature_max']} °C"
)

print(
    f"Minimum temperature : "
    f"{weather['temperature_min']} °C"
)

print(
    f"Mean temperature    : "
    f"{weather['temperature_mean']} °C"
)

print(
    f"Sunshine            : "
    f"{weather['sunshine_sum']:.2f} hours"
)

print(
    f"Rainfall            : "
    f"{weather['precipitation_sum']} mm"
)


print()
print("HISTORICAL MODEL FEATURES")
print("-" * 70)

history = result["historical_features"]

print(
    f"sales_lag_1          : "
    f"{history['sales_lag_1']:.6f}"
)

print(
    f"sales_lag_7          : "
    f"{history['sales_lag_7']:.6f}"
)

print(
    f"rolling_mean_7       : "
    f"{history['sales_rolling_mean_7']:.6f}"
)

print(
    f"History source date  : "
    f"{history['source_date']}"
)


print()
print("MODEL")
print("-" * 70)

print(
    f"Model version       : "
    f"{result['model_version']}"
)

print(
    f"Scaled prediction   : "
    f"{result['scaled_prediction']:.6f}"
)


print()
print("OPERATIONAL FOOD PLAN")
print("-" * 70)

print(
    f"Expected demand     : "
    f"{result['expected_portions']} portions"
)

print(
    f"Safety buffer       : "
    f"{result['safety_buffer']} portions"
)

print(
    f"Recommended prepare : "
    f"{result['recommended_portions']} portions"
)

print(
    f"Calibration         : "
    f"{result['calibration_version']}"
)


print()
print("=" * 70)
print("END-TO-END TEST COMPLETED")
print("=" * 70)