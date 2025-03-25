from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class Attachment(BaseModel):
    filename: str
    content_type: str
    content: bytes
    size: int

class EmailThread(BaseModel):
    thread_id: str
    business_id: str
    subject: str
    customer_email: EmailStr
    last_updated: datetime
    messages: List[dict]
    metadata: dict = {}

class InboundEmail(BaseModel):
    business_id: str
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    text: Optional[str]
    html: Optional[str]
    spam_score: Optional[float]
    spam_report: Optional[dict]
    sender_ip: Optional[str]
    attachments: List[Attachment] = []
    headers: dict
    envelope: dict
    thread_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    business_metadata: dict = {}

    class Config:
        arbitrary_types_allowed = True
