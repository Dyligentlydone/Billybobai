from app.db import db
from sqlalchemy import Enum as PgEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

class MessageDirection(enum.Enum):
    inbound = 'inbound'
    outbound = 'outbound'

class MessageStatus(enum.Enum):
    pending = 'pending'
    queued = 'queued'
    scheduled = 'scheduled'
    sent = 'sent'
    delivered = 'delivered'
    failed = 'failed'
    cancelled = 'cancelled'

class MessageChannel(enum.Enum):
    sms = 'sms'
    whatsapp = 'whatsapp'
    email = 'email'

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    direction = db.Column(PgEnum(MessageDirection), nullable=False, default=MessageDirection.inbound)
    channel = db.Column(PgEnum(MessageChannel), nullable=False, default=MessageChannel.sms)
    status = db.Column(PgEnum(MessageStatus), nullable=False, default=MessageStatus.pending)
    body = db.Column(db.Text, nullable=True)
    # Opt-out tracking is now handled by the SMSConsent table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workflow = relationship('Workflow', backref='messages')

    def __repr__(self):
        return f'<Message id={self.id} phone={self.phone_number} status={self.status}>'
