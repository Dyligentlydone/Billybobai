from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create the declarative base
Base = declarative_base()

# Use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize the database with all tables"""
    # Import all models to ensure they're registered
    from app.models.business import Business, BusinessConfig  # noqa
    from app.models.workflow import Workflow, WorkflowExecution, WorkflowNode, WorkflowEdge  # noqa
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
