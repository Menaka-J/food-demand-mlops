
import os

from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "food_demand")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI environment variable is missing.")

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000,
    appname="SmartFoodDemandMLOps",
)

db = client[MONGODB_DATABASE]


def check_mongodb_connection():
    client.admin.command("ping")
    return True


def close_mongodb_connection():
    client.close()
