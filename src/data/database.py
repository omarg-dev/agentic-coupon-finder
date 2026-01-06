import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# TODO: move to an environment variable later
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./storage/coupons.db")

engine = create_engine(
    DATABASE_URL, 
    # FastAPI handles requests in multiple threads. SQLite needs this flag to allow that.
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The Base class for the models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Generator that creates a database session for a request
    and closes it automatically when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()