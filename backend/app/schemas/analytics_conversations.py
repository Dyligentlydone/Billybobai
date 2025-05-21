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
    # CRITICAL: Ensure messages is always a list, with a default empty list
    messages: List[MessageSchema] = []  # Default to empty list, never None or False
    lastMessage: Optional[str]
    lastTimestamp: Optional[str]
    messageCount: Optional[int]
    status: Optional[str]
    lastTime: Optional[str]
    
    class Config:
        # Ensure JSON serialization doesn't drop empty arrays
        json_encoders = {
            list: lambda v: v or []
        }

class ConversationsResponse(BaseModel):
    conversations: List[ConversationSchema]
