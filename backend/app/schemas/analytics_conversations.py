from pydantic import BaseModel
from typing import List, Optional

class MessageSchema(BaseModel):
    id: str
    content: str
    createdAt: Optional[str]
    direction: Optional[str]
    status: Optional[str]
    phoneNumber: Optional[str]
    aiConfidence: Optional[float]
    templateUsed: Optional[str]

class ConversationSchema(BaseModel):
    id: str
    phoneNumber: Optional[str]
    messages: List[MessageSchema]
    lastMessage: Optional[str]
    lastTimestamp: Optional[str]
    messageCount: Optional[int]
    status: Optional[str]
    lastTime: Optional[str]
