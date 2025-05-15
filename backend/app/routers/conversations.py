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

# Initialize clients with lazy loading to handle missing credentials
twilio_client = None
zendesk_client = None

def get_twilio_client():
    """Get Twilio client with lazy initialization and error handling."""
    global twilio_client
    
    if twilio_client is None:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if account_sid and auth_token:
            try:
                twilio_client = Client(account_sid, auth_token)
                print(f"Twilio client initialized successfully with account SID: {account_sid[:5]}...")
            except Exception as e:
                print(f"Error initializing Twilio client: {str(e)}")
                # Return a stub client that won't crash the app
                return None
        else:
            print("Twilio credentials not found in environment variables")
            return None
            
    return twilio_client

def get_zendesk_client():
    """Get Zendesk client with lazy initialization and error handling."""
    global zendesk_client
    
    if zendesk_client is None:
        subdomain = os.getenv("ZENDESK_SUBDOMAIN")
        email = os.getenv("ZENDESK_EMAIL")
        api_token = os.getenv("ZENDESK_API_TOKEN")
        
        if subdomain and email and api_token:
            try:
                zendesk_client = Zendesk(subdomain, email, api_token)
                print(f"Zendesk client initialized successfully for subdomain: {subdomain}")
            except Exception as e:
                print(f"Error initializing Zendesk client: {str(e)}")
                return None
        else:
            print("Zendesk credentials not found in environment variables")
            return None
            
    return zendesk_client

def get_twilio_messages(business_id: str, phone_number: str = None, days: int = 7):
    """Get messages from Twilio for a specific business and optional phone number."""
    try:
        # Get the Twilio client
        client = get_twilio_client()
        if not client:
            print(f"Unable to get Twilio messages: Twilio client is not available")
            return []
            
        # Get messages from the last X days
        date_filter = datetime.utcnow() - timedelta(days=days)
        
        # Build filter parameters
        params = {
            "date_sent_after": date_filter.isoformat(),
            "to": phone_number if phone_number else None,
        }
        
        # Get messages from Twilio
        messages = client.messages.list(**{k: v for k, v in params.items() if v})
        
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
        # Get the Zendesk client
        client = get_zendesk_client()
        if not client:
            print(f"Unable to get Zendesk tickets: Zendesk client is not available")
            return []
            
        query = f"type:ticket organization:{business_id}"
        if phone_number:
            query += f" phone:{phone_number}"
            
        # Search tickets in Zendesk
        try:
            tickets = client.search(query=query)
        except Exception as e:
            print(f"Error searching Zendesk tickets: {str(e)}")
            return []
        
        messages = []
        for ticket in tickets:
            # Get comments for each ticket
            try:
                comments = client.tickets.comments(ticket.id)
            except Exception as e:
                print(f"Error getting comments for ticket {ticket.id}: {str(e)}")
                continue
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
        
        # Get the Twilio client
        client = get_twilio_client()
        if not client:
            print(f"Unable to send Twilio message: Twilio client is not available")
            return {"error": "Twilio client not available", "status": "failed"}

        # Send message via Twilio
        message = client.messages.create(
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
