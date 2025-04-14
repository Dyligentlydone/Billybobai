from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from config.database import Base
import uuid

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MessageMetric(BaseModel):
    """Message metrics for tracking automation performance"""
    __tablename__ = 'message_metrics'

    business_id = Column(String(36), nullable=False)
    workflow_id = Column(String(36), nullable=False)
    message_sid = Column(String(255), nullable=True)
    response_time = Column(String(50), nullable=True)
    ai_time = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False)
    metrics = Column(JSON, nullable=True)
