import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:PQfalVBeDPVwbHFcnEiIHyNKYjNNjorG@caboose.proxy.rlwy.net:46405/railway"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

def init_db():
    """Initialize the database, creating all tables."""
    # Import all models to ensure they're registered
    from app.models import User, APIIntegration, Workflow, Message, WorkflowExecution
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
