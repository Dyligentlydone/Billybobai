"""
SQLAlchemy models for business-related functionality.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Business(Base):
    """Model for business entities."""
    __tablename__ = 'businesses'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False)
    status = Column(String(50), default='active')  # active, inactive, suspended
    config = Column(JSON)  # Stores BusinessConfig as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship('User', back_populates='business')
    workflows = relationship('Workflow', back_populates='business')
    email_threads = relationship('EmailThread', back_populates='business')
    inbound_emails = relationship('InboundEmail', back_populates='business')
    integrations = relationship('Integration', back_populates='business')

    def __repr__(self):
        return f'<Business {self.name}>'
