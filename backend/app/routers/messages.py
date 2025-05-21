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
    import logging
    logger = logging.getLogger("uvicorn")
    
    # Debug: Log the incoming request
    logger.info(f"[DEBUG] Messages API: Request for conversation_id={conversation_id}")
    
    # Debug: Check a sample of conversation IDs in the database
    sample_messages = db.query(Message).limit(5).all()
    sample_conv_ids = [getattr(m, 'conversation_id', None) for m in sample_messages]
    sample_phone_numbers = [getattr(m, 'phone_number', None) for m in sample_messages]
    logger.info(f"[DEBUG] Messages API: Sample conversation_ids in database: {sample_conv_ids}")
    logger.info(f"[DEBUG] Messages API: Sample phone numbers in database: {sample_phone_numbers}")
    
    # Try to find a conversation in the analytics output to get a phone number
    messages = []
    # Try conversation_id first
    messages_by_id = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    logger.info(f"[DEBUG] Messages API: Found {len(messages_by_id)} messages using conversation_id")
    
    if messages_by_id:
        messages = messages_by_id
    else:
        # We couldn't find messages by conversation_id, let's try to see if this ID maps to a phone number
        # This assumes the phone number is encoded in the conversation ID or has a relationship
        # Let's check analytics conversations to see if there's a mapping
        try:
            # First check if the ID is being used directly as a phone number
            if conversation_id.startswith("+"):
                logger.info(f"[DEBUG] Treating ID as a phone number directly: {conversation_id}")
                phone_number = conversation_id
            else:
                # Try to see if it's a valid UUID format (typical of our analytics conversation IDs)
                # If so, look up the corresponding conversation from analytics to find its phone
                from ..routers.analytics import get_sms_conversation_metrics
                all_conversations = get_sms_conversation_metrics("dummy_business_id", db)  # This returns all convos
                matching_convo = None
                
                for convo in all_conversations["conversations"]:
                    if convo.get("id") == conversation_id:
                        matching_convo = convo
                        break
                
                if matching_convo:
                    phone_number = matching_convo.get("phoneNumber")
                    logger.info(f"[DEBUG] Found matching phone number {phone_number} for conversation {conversation_id}")
                else:
                    logger.warning(f"[DEBUG] Could not find conversation {conversation_id} in analytics data")
                    phone_number = None
            
            if phone_number:
                # Try to fetch messages by phone number instead
                messages_by_phone = (
                    db.query(Message)
                    .filter(Message.phone_number == phone_number)
                    .order_by(Message.created_at.asc())
                    .all()
                )
                logger.info(f"[DEBUG] Messages API: Found {len(messages_by_phone)} messages using phone number {phone_number}")
                messages = messages_by_phone
        except Exception as e:
            logger.error(f"[DEBUG] Error trying alternative lookup methods: {str(e)}")
            # Continue with empty messages list
    
    if not messages:
        logger.warning(f"[DEBUG] Messages API: NO MESSAGES FOUND for conversation_id={conversation_id}")

# Also add a direct phone number endpoint to make it easier
@router.get("/phone/{phone_number}", response_model=ConversationMessagesResponse)
def get_messages_by_phone(phone_number: str, db: Session = Depends(get_db)):
    """
    Get all messages for a specific phone number.
    """
    import logging
    logger = logging.getLogger("uvicorn")
    
    logger.info(f"[DEBUG] Messages API: Request for phone_number={phone_number}")
    
    messages = (
        db.query(Message)
        .filter(Message.phone_number == phone_number)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    logger.info(f"[DEBUG] Messages API: Found {len(messages)} messages for phone_number={phone_number}")
    
    # Debug: Log the number of messages found
    logger.info(f"[DEBUG] Messages API: Found {len(messages)} messages for conversation_id={conversation_id}")
    if messages:
        logger.info(f"[DEBUG] Messages API: First message ID: {messages[0].id}")
    else:
        logger.warning(f"[DEBUG] Messages API: NO MESSAGES FOUND for conversation_id={conversation_id}")
    
    
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
