from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import Session

db = SQLAlchemy()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Import the FastAPI database session functions for compatibility
from config.database import SessionLocal

# Function for FastAPI dependency injection
def get_db():
    """Get a database session - FastAPI compatible implementation."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# All models should import db and get_db from here