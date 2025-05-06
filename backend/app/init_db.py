from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.db import db

# Use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

def init_database():
    """Initialize the database with all tables"""
    engine = create_engine(DATABASE_URL)
    
    # Import all models to ensure they're registered
    from app.models.business import Business, BusinessConfig
    from app.models.workflow import Workflow, WorkflowExecution, WorkflowNode, WorkflowEdge
    
    # Create all tables
    db.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal

if __name__ == "__main__":
    print("Initializing database...")
    engine, Session = init_database()
    print("Database initialized successfully!")
