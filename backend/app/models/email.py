from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from ..database import db

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('inbound_emails.id'))
    filename = Column(String(255))
    content_type = Column(String(100))
    content = Column(LargeBinary)
    size = Column(Integer)

class EmailThread(db.Model):
    __tablename__ = 'email_threads'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(255), unique=True, index=True)
    business_id = Column(String(255))
    subject = Column(String(255))
    customer_email = Column(String(255))
    last_updated = Column(DateTime, default=datetime.utcnow)
    messages = Column(JSON)
    metadata = Column(JSON, default={})

class InboundEmail(db.Model):
    __tablename__ = 'inbound_emails'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(String(255))
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
    
    attachments = relationship('Attachment', backref='email')
