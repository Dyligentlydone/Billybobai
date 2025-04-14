"""
Base integration model that all specific integrations inherit from.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..base import Base
from ..schemas.integration import IntegrationType, IntegrationStatus

class Integration(Base):
    """Base model for all integrations."""
    __tablename__ = 'integrations'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(IntegrationType), nullable=False)
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING)
    config = Column(JSON, nullable=False)
    integration_metadata = Column(JSON, default={})  # Renamed from metadata to integration_metadata
    last_used = Column(DateTime)
    error_message = Column(String)
    business_id = Column(String(255), ForeignKey('businesses.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship('Business', back_populates='integrations')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': None
    }
