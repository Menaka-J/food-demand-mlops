import os

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.server_api import ServerApi


MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "food_demand")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing. Set it in your environment."
    )

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=10000,
)

database = client[MONGODB_DATABASE]

prediction_collection = database["prediction_records"]
calibration_collection = database["canteen_calibrations"]


def initialize_database():
    """Check connectivity and create useful indexes."""

    client.admin.command("ping")

    # One prediction per canteen per prediction date.
    prediction_collection.create_index(
        [
            ("store_id", ASCENDING),
            ("prediction_date", ASCENDING),
        ],
        unique=True,
        name="unique_canteen_prediction_date",
    )

    prediction_collection.create_index(
        [("prediction_date", DESCENDING)],
        name="prediction_date_index",
    )

    prediction_collection.create_index(
        [
            ("store_id", ASCENDING),
            ("actual_portions", ASCENDING),
        ],
        name="canteen_actuals_index",
    )

    calibration_collection.create_index(
        [("store_id", ASCENDING)],
        unique=True,
        name="unique_canteen_calibration",
    )

    print("MongoDB connected successfully.")
    print(f"Database: {MONGODB_DATABASE}")


if __name__ == "__main__":
    initialize_database()