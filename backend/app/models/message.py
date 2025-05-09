from app.db import db
from sqlalchemy import Enum as PgEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

class MessageDirection(enum.Enum):
    INBOUND = 'INBOUND'
    OUTBOUND = 'OUTBOUND'

class MessageStatus(enum.Enum):
    PENDING = 'PENDING'
    QUEUED = 'QUEUED'
    SCHEDULED = 'SCHEDULED'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'

class MessageChannel(enum.Enum):
    SMS = 'SMS'
    WHATSAPP = 'WHATSAPP'
    EMAIL = 'EMAIL'

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    direction = db.Column(PgEnum(MessageDirection), nullable=False, default=MessageDirection.INBOUND)
    channel = db.Column(PgEnum(MessageChannel), nullable=False, default=MessageChannel.SMS)
    status = db.Column(PgEnum(MessageStatus), nullable=False, default=MessageStatus.PENDING)
    content = db.Column(db.String(2000), nullable=True)  # Primary field used by the code
    body = db.Column(db.Text, nullable=True)             # Added field for compatibility
    # Conversation tracking fields
    conversation_id = db.Column(db.String(36), nullable=True, index=True)  # Group messages in conversations
    is_first_in_conversation = db.Column(db.Boolean, default=False)        # Flag for conversation starters
    response_to_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)  # For threading
    # Opt-out tracking is now handled by the SMSConsent table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workflow = relationship('Workflow', backref='messages')

    def __repr__(self):
        return f'<Message id={self.id} phone={self.phone_number} status={self.status}>'
