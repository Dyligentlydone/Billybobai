from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, Float, Boolean, Index
from sqlalchemy.orm import relationship, backref
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

class CustomerSentiment(enum.Enum):
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'
    NEGATIVE = 'negative'

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

    # Analytics fields
    ai_confidence = Column(Float)  # Confidence score of AI response
    response_time = Column(Integer)  # Time taken to generate response in ms
    customer_sentiment = Column(Enum(CustomerSentiment))  # Analyzed sentiment
    template_used = Column(String(255))  # Which response template was used
    processing_attempts = Column(Integer, default=0)  # Number of retry attempts
    error_message = Column(String)  # Store any error messages

    # New conversation threading fields
    conversation_id = Column(String(255), index=True)  # Group messages in same conversation
    phone_number = Column(String(20), index=True)      # Store the customer's phone number
    topic = Column(String(100))                        # AI-categorized topic
    is_first_in_conversation = Column(Boolean, default=False)
    response_to_message_id = Column(Integer, ForeignKey('messages.id'), nullable=True)

    # Relationships
    workflow = relationship('Workflow', back_populates='messages')
    responses = relationship('Message', 
                           backref=backref('parent', remote_side=[id]),
                           foreign_keys=[response_to_message_id])

    def __repr__(self):
        return f'<Message {self.channel}:{self.direction}>'
