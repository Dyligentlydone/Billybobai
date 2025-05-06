"""
SQLAlchemy models for email-related functionality.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from .base import Base

class Attachment(Base):
    """Model for email attachments."""
    __tablename__ = 'attachments'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('inbound_emails.id'))
    filename = Column(String(255))
    content_type = Column(String(100))
    content = Column(LargeBinary)
    size = Column(Integer)

    # Relationship
    email = relationship('InboundEmail', back_populates='attachments')

class EmailThread(Base):
    """Model for email conversation threads."""
    __tablename__ = 'email_threads'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(255), unique=True, index=True)
    business_id = Column(String(255), ForeignKey('businesses.id'))
    subject = Column(String(255))
    customer_email = Column(String(255))
    last_updated = Column(DateTime, default=datetime.utcnow)
    messages = Column(JSON)
    thread_metadata = Column(JSON, default={})  # Renamed from metadata to thread_metadata

    # Relationships
    business = relationship('Business')
    inbound_emails = relationship('InboundEmail')

class InboundEmail(Base):
    """Model for incoming emails."""
    __tablename__ = 'inbound_emails'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    business_id = Column(String(255), ForeignKey('businesses.id'))
    thread_id = Column(String(255), ForeignKey('email_threads.thread_id'))
    from_email = Column(String(255))
    to_email = Column(String(255))
    subject = Column(String(255))
    text = Column(String)
    html = Column(String)
    spam_score = Column(String)
    spam_report = Column(JSON)
    sender_ip = Column(String)
    headers = Column(JSON)
    envelope = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    business_metadata = Column(JSON, default={})

    # Relationships
    attachments = relationship('Attachment', back_populates='email')
    thread = relationship('EmailThread')
    # Remove back_populates to avoid circular dependency issues
    business = relationship('Business')
