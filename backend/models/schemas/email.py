"""
Pydantic schemas for email-related models.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr

class AttachmentSchema(BaseModel):
    """Schema for email attachments."""
    filename: str
    content_type: str
    content: bytes
    size: int

    class Config:
        from_attributes = True

class EmailThreadSchema(BaseModel):
    """Schema for email conversation threads."""
    thread_id: str
    business_id: str
    subject: str
    customer_email: EmailStr
    last_updated: datetime
    messages: List[Dict]
    metadata: Dict = {}

    class Config:
        from_attributes = True

class InboundEmailSchema(BaseModel):
    """Schema for incoming emails."""
    business_id: str
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    text: Optional[str]
    html: Optional[str]
    spam_score: Optional[float]
    spam_report: Optional[Dict]
    sender_ip: Optional[str]
    attachments: List[AttachmentSchema] = []
    headers: Dict
    envelope: Dict
    thread_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    business_metadata: Dict = {}

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
