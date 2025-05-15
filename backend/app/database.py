"""
Database module for the application.
This module provides the database connection and session management.
"""
from app.db import db
from sqlalchemy.orm import Session

# Re-export get_db from config.database to provide backward compatibility
from config.database import get_db, SessionLocal, Base, engine, init_db

# This file is now a pass-through for backward compatibility
# Alternative get_db implementation if needed for Flask compatibility
def get_session():
    """Get a new database session for Flask context."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e
