from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class MessageDirection(enum.Enum):
    INBOUND = 'inbound'
    OUTBOUND = 'outbound'

class MessageChannel(enum.Enum):
    SMS = 'sms'
    VOICE = 'voice'
    EMAIL = 'email'

class MessageStatus(enum.Enum):
    PENDING = 'pending'
    SENT = 'sent'
    DELIVERED = 'delivered'
    FAILED = 'failed'

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(255), ForeignKey('workflows.id'), nullable=False)
    direction = Column(Enum(MessageDirection), nullable=False)
    channel = Column(Enum(MessageChannel), nullable=False)
    content = Column(String(2000), nullable=False)
    message_metadata = Column(JSON)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workflow = relationship('Workflow', back_populates='messages')

    def __repr__(self):
        return f'<Message {self.channel}:{self.direction}>'
