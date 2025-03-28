from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    id: str
    content: str
    timestamp: datetime
    from_: str
    to: str
    direction: str
    source: str
    status: str
    media_urls: Optional[List[str]] = None
    zendesk_ticket_id: Optional[str] = None

class Conversation(BaseModel):
    id: str
    customer_number: str
    customer_name: Optional[str] = None
    last_message: Message
    unread_count: int
    status: str
    zendesk_ticket_url: Optional[str] = None
    tags: List[str]
    updated_at: datetime

class ConversationsResponse(BaseModel):
    conversations: List[Conversation]
    total_count: int
    has_more: bool

class ConversationMessagesResponse(BaseModel):
    messages: List[Message]
    has_more: bool
    next_cursor: Optional[str] = None
