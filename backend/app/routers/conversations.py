from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..schemas.conversations import (
    Message,
    Conversation,
    ConversationsResponse,
    ConversationMessagesResponse,
)
from twilio.rest import Client
from zendesk.api import Zendesk
import os
from datetime import datetime, timedelta

router = APIRouter()

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Initialize Zendesk client
zendesk_client = Zendesk(
    os.getenv("ZENDESK_SUBDOMAIN"),
    os.getenv("ZENDESK_EMAIL"),
    os.getenv("ZENDESK_API_TOKEN")
)

def get_twilio_messages(business_id: str, phone_number: str = None, days: int = 7):
    """Get messages from Twilio for a specific business and optional phone number."""
    try:
        # Get messages from the last X days
        date_filter = datetime.utcnow() - timedelta(days=days)
        
        # Build filter parameters
        params = {
            "date_sent_after": date_filter.isoformat(),
            "to": phone_number if phone_number else None,
        }
        
        # Get messages from Twilio
        messages = twilio_client.messages.list(**{k: v for k, v in params.items() if v})
        
        return [
            Message(
                id=msg.sid,
                content=msg.body,
                timestamp=msg.date_sent,
                from_=msg.from_,
                to=msg.to,
                direction="inbound" if msg.direction == "inbound" else "outbound",
                source="twilio",
                status=msg.status,
                media_urls=[media.uri for media in msg.media.list()] if msg.num_media != "0" else None
            )
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Twilio messages: {str(e)}")

def get_zendesk_tickets(business_id: str, phone_number: str = None):
    """Get tickets from Zendesk for a specific business and optional phone number."""
    try:
        # Build search query
        query = f"type:ticket organization:{business_id}"
        if phone_number:
            query += f" phone:{phone_number}"
            
        # Search tickets in Zendesk
        tickets = zendesk_client.search(query=query)
        
        messages = []
        for ticket in tickets:
            # Get comments for each ticket
            comments = zendesk_client.tickets.comments(ticket.id)
            for comment in comments:
                if not comment.public:  # Skip internal notes
                    continue
                    
                messages.append(
                    Message(
                        id=str(comment.id),
                        content=comment.body,
                        timestamp=comment.created_at,
                        from_=comment.author_id,
                        to=ticket.requester_id,
                        direction="outbound" if comment.author_id == ticket.assignee_id else "inbound",
                        source="zendesk",
                        status="sent",
                        zendesk_ticket_id=str(ticket.id)
                    )
                )
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Zendesk tickets: {str(e)}")

@router.get("/businesses/{business_id}/conversations", response_model=ConversationsResponse)
async def list_conversations(business_id: str, search: Optional[str] = None):
    """List all conversations for a business with optional search."""
    try:
        # Get messages from both Twilio and Zendesk
        twilio_messages = get_twilio_messages(business_id)
        zendesk_messages = get_zendesk_tickets(business_id)
        
        # Combine and group messages by phone number/customer
        conversations = {}
        for msg in twilio_messages + zendesk_messages:
            customer_number = msg.from_ if msg.direction == "inbound" else msg.to
            
            if customer_number not in conversations:
                conversations[customer_number] = {
                    "messages": [],
                    "unread_count": 0,
                    "last_message": None,
                    "zendesk_ticket_url": None
                }
            
            conversations[customer_number]["messages"].append(msg)
            if msg.direction == "inbound" and msg.status != "read":
                conversations[customer_number]["unread_count"] += 1
            
            # Update last message if this is more recent
            if (not conversations[customer_number]["last_message"] or
                msg.timestamp > conversations[customer_number]["last_message"].timestamp):
                conversations[customer_number]["last_message"] = msg
            
            # Store Zendesk ticket URL if available
            if msg.source == "zendesk" and msg.zendesk_ticket_id:
                conversations[customer_number]["zendesk_ticket_url"] = (
                    f"https://{os.getenv('ZENDESK_SUBDOMAIN')}.zendesk.com/tickets/{msg.zendesk_ticket_id}"
                )
        
        # Convert to list of Conversation objects
        conversation_list = [
            Conversation(
                id=f"{business_id}:{number}",
                customer_number=number,
                last_message=data["last_message"],
                unread_count=data["unread_count"],
                status="active" if data["unread_count"] > 0 else "resolved",
                zendesk_ticket_url=data["zendesk_ticket_url"],
                tags=[],  # TODO: Implement tagging system
                updated_at=data["last_message"].timestamp
            )
            for number, data in conversations.items()
        ]
        
        # Apply search filter if provided
        if search:
            conversation_list = [
                conv for conv in conversation_list
                if search.lower() in conv.customer_number.lower()
            ]
        
        # Sort by most recent first
        conversation_list.sort(key=lambda x: x.updated_at, reverse=True)
        
        return ConversationsResponse(
            conversations=conversation_list,
            total_count=len(conversation_list),
            has_more=False  # TODO: Implement pagination
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(conversation_id: str):
    """Get messages for a specific conversation."""
    try:
        # Parse business_id and phone_number from conversation_id
        business_id, phone_number = conversation_id.split(":")
        
        # Get messages from both sources
        twilio_messages = get_twilio_messages(business_id, phone_number)
        zendesk_messages = get_zendesk_tickets(business_id, phone_number)
        
        # Combine and sort messages by timestamp
        all_messages = twilio_messages + zendesk_messages
        all_messages.sort(key=lambda x: x.timestamp)
        
        return ConversationMessagesResponse(
            messages=all_messages,
            has_more=False  # TODO: Implement pagination
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, content: str):
    """Send a new message in a conversation."""
    try:
        # Parse business_id and phone_number from conversation_id
        business_id, phone_number = conversation_id.split(":")
        
        # Send message via Twilio
        message = twilio_client.messages.create(
            body=content,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=phone_number
        )
        
        return {
            "id": message.sid,
            "status": "sent",
            "timestamp": message.date_sent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
