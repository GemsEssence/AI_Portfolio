import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Base

load_dotenv()

DB = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}


def get_engine():
    try:
        url = (
            f"postgresql+psycopg2://{DB['user']}:{DB['password']}"
            f"@{DB['host']}:{DB['port']}/{DB['name']}"
        )

        engine = create_engine(url)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("✅ PostgreSQL Connected")
        return engine

    except Exception as e:
        print("⚠️ PostgreSQL Failed — using SQLite fallback", e)

        engine = create_engine("sqlite:///:memory:")

        # Create tables but DO NOT insert mock data
        Base.metadata.create_all(engine)

        return engine


engine = get_engine()
SessionLocal = sessionmaker(bind=engine)
