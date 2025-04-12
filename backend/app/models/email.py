from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from ..database import db

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('inbound_emails.id'))
    filename = Column(String(255))
    content_type = Column(String(100))
    content = Column(LargeBinary)
    size = Column(Integer)

class AttachmentModel(BaseModel):
    filename: str
    content_type: str
    content: bytes
    size: int

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

class EmailThreadModel(BaseModel):
    thread_id: str
    business_id: str
    subject: str
    customer_email: EmailStr
    last_updated: datetime
    messages: List[dict]
    metadata: dict = {}

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

class InboundEmailModel(BaseModel):
    business_id: str
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    text: Optional[str]
    html: Optional[str]
    spam_score: Optional[float]
    spam_report: Optional[dict]
    sender_ip: Optional[str]
    attachments: List[AttachmentModel] = []
    headers: dict
    envelope: dict
    thread_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    business_metadata: dict = {}

    class Config:
        arbitrary_types_allowed = True
