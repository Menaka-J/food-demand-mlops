
from app.mongodb import (
    check_mongodb_connection,
    close_mongodb_connection,
    db,
)

try:
    check_mongodb_connection()
    print("MongoDB Atlas connection successful!")
    print("Database:", db.name)
finally:
    close_mongodb_connection()
