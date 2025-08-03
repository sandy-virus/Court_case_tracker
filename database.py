from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Use normal SQLite
DATABASE_URL = "sqlite:///court_cases.db"

# Create a synchronous engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
