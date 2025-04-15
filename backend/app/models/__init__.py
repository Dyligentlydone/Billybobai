"""
Models package for the application.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

Base = declarative_base()

# Import all models after Base is defined
from .business import Business, BusinessConfig  # noqa
from .workflow import Workflow, WorkflowExecution, WorkflowNode, WorkflowEdge  # noqa

# Create engine and session
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = [
    'Workflow',
    'WorkflowExecution',
    'WorkflowNode',
    'WorkflowEdge',
    'Business',
    'BusinessConfig'
]