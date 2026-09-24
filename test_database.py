from sqlalchemy import inspect

from app.database import engine


inspector = inspect(engine)

tables = inspector.get_table_names()

print("=" * 60)
print("DATABASE TEST")
print("=" * 60)

print()

print("Database tables:")

for table in tables:
    print(f"- {table}")

print()

columns = inspector.get_columns(
    "prediction_records"
)

print("prediction_records columns:")

for column in columns:
    print(
        f"- {column['name']} "
        f"({column['type']})"
    )

print()
print("=" * 60)
print("DATABASE TEST COMPLETED")
print("=" * 60)