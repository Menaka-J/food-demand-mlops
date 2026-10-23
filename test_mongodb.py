from app.database import initialize_database, database

initialize_database()

print("MongoDB connection successful!")
print("Database:", database.name)
print("Collections:", database.list_collection_names())