import pandas as pd


def create_prediction_features(
    current_date,
    store,
    is_state_holiday,
    is_school_holiday,
    is_special_day,
    temperature_max,
    temperature_min,
    temperature_mean,
    sunshine_sum,
    precipitation_sum,
    historical_records
):
    history = pd.DataFrame(historical_records)

    if history.empty:
        raise ValueError(
            "No historical sales data available for this store."
        )

    history["date"] = pd.to_datetime(history["date"])

    history = history.sort_values("date")

    sales = history["actual_sales"].dropna()

    if len(sales) < 7:
        raise ValueError(
            "At least 7 historical sales observations are required."
        )

    sales_lag_1 = sales.iloc[-1]
    sales_lag_7 = sales.iloc[-7]

    sales_rolling_mean_7 = sales.iloc[-7:].mean()

    current_date = pd.to_datetime(current_date)

    features = {
        "store": store,

        "is_state_holiday": is_state_holiday,
        "is_school_holiday": is_school_holiday,
        "is_special_day": is_special_day,

        "temperature_max": temperature_max,
        "temperature_min": temperature_min,
        "temperature_mean": temperature_mean,

        "sunshine_sum": sunshine_sum,
        "precipitation_sum": precipitation_sum,

        "year": current_date.year,
        "month": current_date.month,
        "day": current_date.day,
        "day_of_week": current_date.dayofweek,
        "week_of_year": current_date.isocalendar().week,
        "quarter": current_date.quarter,
        "is_weekend": int(current_date.dayofweek >= 5),

        "sales_lag_1": sales_lag_1,
        "sales_lag_7": sales_lag_7,
        "sales_rolling_mean_7": sales_rolling_mean_7
    }

    return pd.DataFrame([features])