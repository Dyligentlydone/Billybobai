from typing import Dict, List, Optional
import os
from zendesk import Zendesk
from pydantic import BaseModel

class TicketRequest(BaseModel):
    subject: str
    description: str
    priority: str = "normal"  # low, normal, high, urgent
    type: str = "question"    # question, incident, problem, task
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict] = None
    assignee_email: Optional[str] = None
    requester_email: Optional[str] = None

class ZendeskService:
    def __init__(self):
        self.client = Zendesk(
            subdomain=os.getenv('ZENDESK_SUBDOMAIN'),
            email=os.getenv('ZENDESK_EMAIL'),
            token=os.getenv('ZENDESK_API_TOKEN')
        )

    async def create_ticket(self, request: TicketRequest) -> Dict:
        """Create a new ticket in Zendesk."""
        try:
            ticket_data = {
                "ticket": {
                    "subject": request.subject,
                    "comment": {"body": request.description},
                    "priority": request.priority,
                    "type": request.type
                }
            }

            if request.tags:
                ticket_data["ticket"]["tags"] = request.tags

            if request.custom_fields:
                ticket_data["ticket"]["custom_fields"] = request.custom_fields

            if request.assignee_email:
                assignee = await self._find_user(request.assignee_email)
                if assignee:
                    ticket_data["ticket"]["assignee_id"] = assignee["id"]

            if request.requester_email:
                requester = await self._find_or_create_user(request.requester_email)
                ticket_data["ticket"]["requester_id"] = requester["id"]

            response = await self.client.tickets.create(ticket_data)
            return {
                "id": response["ticket"]["id"],
                "status": response["ticket"]["status"],
                "priority": response["ticket"]["priority"],
                "url": response["ticket"]["url"]
            }
        except Exception as e:
            raise Exception(f"Zendesk error: {str(e)}")

    async def update_ticket(self, ticket_id: int, updates: Dict) -> Dict:
        """Update an existing ticket in Zendesk."""
        try:
            ticket_data = {"ticket": updates}
            response = await self.client.tickets.update(ticket_id, ticket_data)
            return {
                "id": response["ticket"]["id"],
                "status": response["ticket"]["status"],
                "priority": response["ticket"]["priority"],
                "url": response["ticket"]["url"]
            }
        except Exception as e:
            raise Exception(f"Failed to update ticket: {str(e)}")

    async def add_comment(self, ticket_id: int, comment: str, public: bool = True) -> Dict:
        """Add a comment to an existing ticket."""
        try:
            response = await self.client.tickets.update(
                ticket_id,
                {
                    "ticket": {
                        "comment": {
                            "body": comment,
                            "public": public
                        }
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
        try:
            response = await self.client.users.search(query=email)
            users = response.get("users", [])
            return users[0] if users else None
        except Exception:
            return None

    async def _find_or_create_user(self, email: str) -> Dict:
        """Find a user by email or create if not exists."""
        user = await self._find_user(email)
        if user:
            return user

        try:
            response = await self.client.users.create({
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
