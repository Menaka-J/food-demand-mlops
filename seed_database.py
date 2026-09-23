import pandas as pd

from app.database import SessionLocal, Base, engine
from app.models import DailyRecord


Base.metadata.create_all(bind=engine)

TRAIN_PATH = "data/raw/train.csv"

df = pd.read_csv(TRAIN_PATH)

df["date"] = pd.to_datetime(df["date"])


db = SessionLocal()

try:

    for _, row in df.iterrows():

        existing = (
            db.query(DailyRecord)
            .filter(
                DailyRecord.date == row["date"],
                DailyRecord.store == row["store"]
            )
            .first()
        )

        if existing:
            continue

        record = DailyRecord(

            date=row["date"].date(),
            store=row["store"],

            is_state_holiday=row["is_state_holiday"],
            is_school_holiday=row["is_school_holiday"],
            is_special_day=row["is_special_day"],

            temperature_max=row["temperature_max"],
            temperature_min=row["temperature_min"],
            temperature_mean=row["temperature_mean"],

            sunshine_sum=row["sunshine_sum"],
            precipitation_sum=row["precipitation_sum"],

            actual_sales=row["sales"],
            prediction=None
        )

        db.add(record)

    db.commit()

    print("Historical data loaded successfully.")

finally:

    db.close()