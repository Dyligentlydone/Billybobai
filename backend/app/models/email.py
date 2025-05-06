from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey, LargeBinary
from pydantic import BaseModel, EmailStr
from ..database import db

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('inbound_emails.id'))
    filename = db.Column(db.String(255))
    content_type = db.Column(db.String(100))
    content = db.Column(db.LargeBinary)
    size = db.Column(db.Integer)

class AttachmentModel(BaseModel):
    filename: str
    content_type: str
    content: bytes
    size: int

class EmailThread(db.Model):
    __tablename__ = 'email_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(255), unique=True, index=True)
    # Link to Business
    business_id = db.Column(db.String(255), db.ForeignKey('businesses.id'))
    subject = db.Column(db.String(255))
    customer_email = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.Column(db.JSON)
    thread_metadata = db.Column(db.JSON, default={})  

    # Relationship back to Business
    business = db.relationship('Business', back_populates='email_threads')

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
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.String(255))
    thread_id = db.Column(db.String(255), db.ForeignKey('email_threads.thread_id'))
    from_email = db.Column(db.String(255))
    to_email = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    text = db.Column(db.String)
    html = db.Column(db.String)
    spam_score = db.Column(db.String)
    spam_report = db.Column(db.JSON)
    sender_ip = db.Column(db.String)
    headers = db.Column(db.JSON)
    envelope = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    business_metadata = db.Column(db.JSON, default={})
    
    attachments = db.relationship('Attachment', backref='email')

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
