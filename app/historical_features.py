from pathlib import Path

import pandas as pd


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Public training dataset
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"


class HistoricalFeatureService:
    """
    Provides historical scaled-sales features required by the
    existing ML model.

    IMPORTANT:
    These values come only from the original public dataset.
    Real operational portion counts are NOT used here.
    """

    def __init__(self):
        if not TRAIN_PATH.exists():
            raise FileNotFoundError(
                f"Training dataset not found: {TRAIN_PATH}"
            )

        self.df = pd.read_csv(TRAIN_PATH)

        self.df["date"] = pd.to_datetime(self.df["date"])

        self.df = self.df.sort_values(
            ["store", "date"]
        ).reset_index(drop=True)

        # Calculate the same historical features used
        # during Phase 2 model training.
        self.df["sales_lag_1"] = (
            self.df.groupby("store")["sales"].shift(1)
        )

        self.df["sales_lag_7"] = (
            self.df.groupby("store")["sales"].shift(7)
        )

        self.df["sales_rolling_mean_7"] = (
            self.df.groupby("store")["sales"]
            .shift(1)
            .rolling(window=7)
            .mean()
            .reset_index(level=0, drop=True)
        )

    def get_latest_features(self, store_id: str) -> dict:
        """
        Get the latest valid historical feature values
        available for a particular store.

        These are used as the initial historical context
        before sufficient operational canteen data exists.
        """

        store_df = self.df[
            self.df["store"] == store_id
        ].copy()

        if store_df.empty:
            raise ValueError(
                f"No historical data found for {store_id}"
            )

        valid = store_df.dropna(
            subset=[
                "sales_lag_1",
                "sales_lag_7",
                "sales_rolling_mean_7",
            ]
        )

        if valid.empty:
            raise ValueError(
                f"No valid historical features found for {store_id}"
            )

        latest = valid.iloc[-1]

        return {
            "sales_lag_1": float(latest["sales_lag_1"]),
            "sales_lag_7": float(latest["sales_lag_7"]),
            "sales_rolling_mean_7": float(
                latest["sales_rolling_mean_7"]
            ),
            "source_date": latest["date"].date().isoformat(),
        }

    def get_store_summary(self, store_id: str) -> dict:
        """
        Return historical information for one store.
        """

        store_df = self.df[
            self.df["store"] == store_id
        ].copy()

        if store_df.empty:
            raise ValueError(
                f"No historical data found for {store_id}"
            )

        return {
            "store_id": store_id,
            "rows": len(store_df),
            "start_date": store_df["date"].min().date().isoformat(),
            "end_date": store_df["date"].max().date().isoformat(),
            "mean_sales": float(store_df["sales"].mean()),
            "median_sales": float(store_df["sales"].median()),
        }