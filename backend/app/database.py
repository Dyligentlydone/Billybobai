from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    echo=True
)

Session = sessionmaker(bind=engine)

def init_db():
    Base = db.Model
    # Import models here to ensure they're registered with SQLAlchemy
    from .models.workflow import Workflow, WorkflowExecution, WorkflowNode, WorkflowEdge
    return Base

def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()

# Database dependency
def get_db():
    return get_session()