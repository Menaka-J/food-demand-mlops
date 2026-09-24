from app.database import SessionLocal
from app.models import PredictionRecord


db = SessionLocal()

try:
    deleted = (
        db.query(PredictionRecord)
        .delete()
    )

    db.commit()

    print(
        f"Deleted {deleted} prediction records."
    )

finally:
    db.close()