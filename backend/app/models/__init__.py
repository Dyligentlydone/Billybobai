"""
This module is deprecated. Import models from the root models package instead.
This file exists only for backward compatibility.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

Base = declarative_base()

# Import all models after Base is defined
from .business import Business, BusinessConfig  # noqa
from .workflow import Workflow  # noqa
from .message import Message  # noqa
from .metrics_log import MetricsLog  # noqa
from .workflow_execution import WorkflowExecution  # noqa
from .email import InboundEmail, EmailThread, Attachment  # noqa

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
    'InboundEmail',
    'EmailThread',
    'Attachment',
    'Business',
    'BusinessConfig'
]