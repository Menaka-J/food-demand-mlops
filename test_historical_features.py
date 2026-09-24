from app.historical_features import HistoricalFeatureService


service = HistoricalFeatureService()

print("=" * 70)
print("HISTORICAL FEATURE SERVICE TEST")
print("=" * 70)

for store_id in [
    "store_0",
    "store_1",
    "store_5",
    "store_8",
]:
    print()
    print(f"Store: {store_id}")

    summary = service.get_store_summary(store_id)

    print(f"Rows       : {summary['rows']}")
    print(f"Start date : {summary['start_date']}")
    print(f"End date   : {summary['end_date']}")
    print(f"Mean sales : {summary['mean_sales']:.4f}")
    print(f"Median     : {summary['median_sales']:.4f}")

    features = service.get_latest_features(store_id)

    print("Historical features:")
    print(
        f"  sales_lag_1          = "
        f"{features['sales_lag_1']:.6f}"
    )
    print(
        f"  sales_lag_7          = "
        f"{features['sales_lag_7']:.6f}"
    )
    print(
        f"  sales_rolling_mean_7 = "
        f"{features['sales_rolling_mean_7']:.6f}"
    )
    print(
        f"  source_date           = "
        f"{features['source_date']}"
    )