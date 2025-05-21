from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models import Message
from ..models.workflow import Workflow
from ..schemas.analytics_conversations import MessageSchema
from pydantic import BaseModel

router = APIRouter(prefix="/api/messages", tags=["messages"])

class ConversationMessagesResponse(BaseModel):
    messages: List[MessageSchema]

@router.get("/conversation/{conversation_id}", response_model=ConversationMessagesResponse)
def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get all messages for a specific conversation - simple and direct endpoint.
    """
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    # This is a simple, direct serialization with no complex nested objects
    message_list = [
        {
            "id": str(m.id),
            "content": m.content if hasattr(m, "content") and m.content is not None else "",
            "createdAt": m.created_at.isoformat() if hasattr(m, "created_at") and m.created_at is not None else "",
            "direction": str(getattr(m, "direction", "")) if getattr(m, "direction", None) is not None else "",
            "status": str(getattr(m, "status", "")) if getattr(m, "status", None) is not None else "",
            "phoneNumber": str(getattr(m, "phone_number", "")) if getattr(m, "phone_number", None) is not None else "",
            "aiConfidence": float(getattr(m, "ai_confidence", 0)) if getattr(m, "ai_confidence", None) is not None else None,
            "templateUsed": str(getattr(m, "template_used", "")) if getattr(m, "template_used", None) is not None else ""
        }
        for m in messages
    ]
    
    return {"messages": message_list}
