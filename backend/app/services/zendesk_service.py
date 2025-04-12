import os
from typing import Dict, Optional
from zenpy import Zenpy
from zenpy.lib.exception import ZenpyException
from pydantic import BaseModel

class TicketRequest(BaseModel):
    subject: str
    description: str
    priority: Optional[str] = "normal"
    type: Optional[str] = "question"
    tags: Optional[list[str]] = None
    custom_fields: Optional[Dict] = None
    assignee_email: Optional[str] = None
    requester_email: Optional[str] = None

class ZendeskService:
    def __init__(self):
        subdomain = os.getenv('ZENDESK_SUBDOMAIN')
        email = os.getenv('ZENDESK_EMAIL')
        token = os.getenv('ZENDESK_API_TOKEN')
        
        if subdomain and email and token:
            self.client = Zenpy(
                subdomain=subdomain,
                email=email,
                token=token
            )
        else:
            self.client = None

    async def create_ticket(self, request: TicketRequest) -> Dict:
        """Create a new ticket in Zendesk."""
        if not self.client:
            raise ZenpyException("Zendesk credentials not configured")
            
        try:
            ticket_data = {
                "subject": request.subject,
                "description": request.description,
                "priority": request.priority,
                "type": request.type
            }

            if request.tags:
                ticket_data["tags"] = request.tags

            if request.custom_fields:
                ticket_data["custom_fields"] = request.custom_fields

            if request.assignee_email:
                user = self.client.users.search(email=request.assignee_email)
                if user:
                    ticket_data["assignee_id"] = next(user).id

            if request.requester_email:
                user = self.client.users.search(email=request.requester_email)
                if user:
                    ticket_data["requester_id"] = next(user).id

            ticket = self.client.tickets.create(ticket_data)
            return {"id": ticket.id, "status": "created"}

        except ZenpyException as e:
            raise e

    async def get_ticket(self, ticket_id: int) -> Dict:
        """Get ticket details."""
        if not self.client:
            raise ZenpyException("Zendesk credentials not configured")
            
        try:
            ticket = self.client.tickets(id=ticket_id)
            return {
                "id": ticket.id,
                "status": ticket.status,
                "subject": ticket.subject,
                "description": ticket.description,
                "priority": ticket.priority,
                "type": ticket.type
            }
        except Exception as e:
            raise Exception(f"Failed to get Zendesk ticket: {str(e)}")

    async def update_ticket(self, ticket_id: int, updates: Dict) -> Dict:
        """Update an existing ticket."""
        if not self.client:
            raise ZenpyException("Zendesk credentials not configured")
            
        try:
            ticket = self.client.tickets(id=ticket_id)
            for key, value in updates.items():
                setattr(ticket, key, value)
            updated = self.client.tickets.update(ticket)
            return {
                "id": updated.id,
                "status": updated.status,
                "url": f"https://{os.getenv('ZENDESK_SUBDOMAIN')}.zendesk.com/agent/tickets/{updated.id}"
            }
        except Exception as e:
            raise Exception(f"Failed to update Zendesk ticket: {str(e)}")

    async def add_comment(self, ticket_id: int, comment: str, public: bool = True) -> Dict:
        """Add a comment to an existing ticket."""
        if not self.client:
            raise ZenpyException("Zendesk credentials not configured")
            
        try:
            response = self.client.tickets.update(
                ticket_id,
                {
                    "comment": {
                        "body": comment,
                        "public": public
                    }
                }
            )
            return {
                "id": response["ticket"]["id"],
                "comment_id": response["audit"]["events"][-1]["id"],
                "status": response["ticket"]["status"]
            }
        except Exception as e:
            raise Exception(f"Failed to add comment: {str(e)}")

    async def _find_user(self, email: str) -> Optional[Dict]:
        """Find a user by email."""
        if not self.client:
            raise ZenpyException("Zendesk credentials not configured")
            
        try:
            users = self.client.users(email=email)
            return users[0] if users else None
        except Exception:
            return None

    async def _find_or_create_user(self, email: str) -> Dict:
        """Find a user by email or create if not exists."""
        if not self.client:
            raise ZenpyException("Zendesk credentials not configured")
            
        user = await self._find_user(email)
        if user:
            return user

        try:
            response = self.client.users.create({
                "user": {
                    "email": email,
                    "name": email.split("@")[0]  # Use email username as name
                }
            })
            return response["user"]
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    def validate_webhook(self, request_data: Dict) -> bool:
        """Validate incoming webhook request from Zendesk."""
        # Add validation logic here
        return True
