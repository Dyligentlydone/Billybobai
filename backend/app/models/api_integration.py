"""
API Integration model for storing integration configurations.
"""
from app.db import db
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# SQLAlchemy model for Flask-SQLAlchemy
class APIIntegration(db.Model):
    """API Integration model for Flask-SQLAlchemy."""
    __tablename__ = 'api_integrations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    api_type = db.Column(db.String(50), nullable=False)  # 'twilio', 'zendesk', etc.
    config = db.Column(db.JSON, nullable=False, default={})
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIIntegration {self.name} ({self.api_type})>"

# Base model class for SQLAlchemy ORM (for FastAPI)
Base = declarative_base()

# SQLAlchemy model for FastAPI
class APIIntegrationORM(Base):
    """API Integration model for SQLAlchemy ORM (FastAPI)."""
    __tablename__ = 'api_integrations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    api_type = Column(String(50), nullable=False)  # 'twilio', 'zendesk', etc.
    config = Column(JSON, nullable=False, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIIntegration {self.name} ({self.api_type})>"
