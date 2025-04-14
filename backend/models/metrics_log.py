from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class MetricType(enum.Enum):
    RESPONSE_TIME = 'response_time'
    ERROR_RATE = 'error_rate'
    MESSAGE_VOLUME = 'message_volume'
    AI_CONFIDENCE = 'ai_confidence'
    CUSTOMER_SENTIMENT = 'customer_sentiment'

class MetricsLog(Base):
    __tablename__ = 'metrics_logs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(255), ForeignKey('workflows.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_type = Column(Enum(MetricType), nullable=False)
    value = Column(Float, nullable=False)
    metric_metadata = Column(String)  # Additional context about the metric

    # Relationships
    workflow = relationship('Workflow', back_populates='metrics')

    def __repr__(self):
        return f'<MetricsLog {self.metric_type.value}:{self.value}>'
