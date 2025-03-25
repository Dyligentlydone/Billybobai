from datetime import datetime
from typing import Optional, List
import hashlib
from ..models.email import EmailThread, InboundEmail
from ..database import db

class EmailThreadService:
    def __init__(self):
        self.collection = db.email_threads

    async def get_or_create_thread(self, email: InboundEmail) -> EmailThread:
        """Get existing thread or create new one based on email headers."""
        thread_id = self._extract_thread_id(email)
        
        # Try to find existing thread
        thread = await self.collection.find_one({"thread_id": thread_id})
        
        if thread:
            # Update existing thread
            await self.collection.update_one(
                {"thread_id": thread_id},
                {
                    "$set": {"last_updated": datetime.utcnow()},
                    "$push": {
                        "messages": {
                            "from": email.from_email,
                            "content": email.text or email.html,
                            "timestamp": email.timestamp,
                            "direction": "inbound"
                        }
                    }
                }
            )
        else:
            # Create new thread
            thread = EmailThread(
                thread_id=thread_id,
                subject=email.subject,
                customer_email=email.from_email,
                last_updated=datetime.utcnow(),
                messages=[{
                    "from": email.from_email,
                    "content": email.text or email.html,
                    "timestamp": email.timestamp,
                    "direction": "inbound"
                }]
            )
            await self.collection.insert_one(thread.dict())

        return thread

    def _extract_thread_id(self, email: InboundEmail) -> str:
        """Extract or generate thread ID from email headers."""
        # Try to get thread ID from references or in-reply-to
        thread_id = (
            email.headers.get("references", "").split()[0] or
            email.headers.get("in-reply-to", "")
        )
        
        if not thread_id:
            # Generate new thread ID from email data
            data = f"{email.from_email}{email.subject}{email.timestamp}"
            thread_id = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        return thread_id

    async def get_thread_history(self, thread_id: str) -> Optional[List[dict]]:
        """Get conversation history for a thread."""
        thread = await self.collection.find_one({"thread_id": thread_id})
        return thread["messages"] if thread else None

    async def add_response_to_thread(self, thread_id: str, response_content: str):
        """Add AI response to thread history."""
        await self.collection.update_one(
            {"thread_id": thread_id},
            {
                "$set": {"last_updated": datetime.utcnow()},
                "$push": {
                    "messages": {
                        "from": "ai_assistant",
                        "content": response_content,
                        "timestamp": datetime.utcnow(),
                        "direction": "outbound"
                    }
                }
            }
        )
