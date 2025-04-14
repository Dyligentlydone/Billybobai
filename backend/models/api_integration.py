from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from .base import Base

class APIIntegration(Base):
    __tablename__ = 'api_integrations'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_name = Column(String(50), nullable=False)
    credentials = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='api_integrations')

    def __repr__(self):
        return f'<APIIntegration {self.service_name}>'
