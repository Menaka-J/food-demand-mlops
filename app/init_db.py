from app.database import engine
from app.models import Base


def initialize_database():
    Base.metadata.create_all(
        bind=engine
    )

    print("Database initialized successfully.")
    print(f"Database: {engine.url}")


if __name__ == "__main__":
    initialize_database()