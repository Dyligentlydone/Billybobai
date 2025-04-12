from datetime import datetime
from typing import Optional, List
import hashlib
from ..models.email import EmailThread, InboundEmail, EmailThreadModel, InboundEmailModel
from ..database import db

class EmailThreadService:
    def __init__(self):
        pass  # No initialization needed, using SQLAlchemy models directly

    async def get_or_create_thread(self, email: InboundEmailModel) -> EmailThreadModel:
        """Get existing thread or create new one based on email headers."""
        thread_id = self._extract_thread_id(email)
        
        # Try to find existing thread
        thread = EmailThread.query.filter_by(thread_id=thread_id).first()
        
        if not thread:
            # Create new thread
            thread = EmailThread(
                thread_id=thread_id,
                business_id=email.business_id,
                subject=email.subject,
                customer_email=email.from_email,
                last_updated=datetime.utcnow(),
                messages=[],
                thread_metadata={}
            )
            db.session.add(thread)
            db.session.commit()
        else:
            # Update existing thread
            thread.last_updated = datetime.utcnow()
            db.session.commit()

        # Add message to thread
        messages = thread.messages or []
        messages.append({
            "from": email.from_email,
            "content": email.text or email.html,
            "timestamp": email.timestamp.isoformat() if email.timestamp else datetime.utcnow().isoformat(),
            "direction": "inbound"
        })
        thread.messages = messages
        db.session.commit()

        # Convert to Pydantic model for API response
        return EmailThreadModel(
            thread_id=thread.thread_id,
            business_id=thread.business_id,
            subject=thread.subject,
            customer_email=thread.customer_email,
            last_updated=thread.last_updated,
            messages=thread.messages,
            metadata=thread.thread_metadata or {}
        )

    def _extract_thread_id(self, email: InboundEmailModel) -> str:
        """Extract or generate thread ID from email headers."""
        # Try to get thread ID from headers
        headers = email.headers or {}
        references = headers.get('References', '')
        in_reply_to = headers.get('In-Reply-To', '')
        message_id = headers.get('Message-ID', '')
        
        # If this is a reply, use the References or In-Reply-To header
        if references:
            return hashlib.md5(references.encode()).hexdigest()
        elif in_reply_to:
            return hashlib.md5(in_reply_to.encode()).hexdigest()
            
        # For new threads, use Message-ID or generate a new ID
        if message_id:
            return hashlib.md5(message_id.encode()).hexdigest()
        else:
            # Generate a new thread ID from email metadata
            thread_data = f"{email.from_email}:{email.to_email}:{email.subject}:{datetime.utcnow().isoformat()}"
            return hashlib.md5(thread_data.encode()).hexdigest()

    async def get_thread_history(self, thread_id: str) -> Optional[List[dict]]:
        """Get conversation history for a thread."""
        thread = EmailThread.query.filter_by(thread_id=thread_id).first()
        return thread.messages if thread else None

    async def add_response_to_thread(self, thread_id: str, response_content: str):
        """Add AI response to thread history."""
        thread = EmailThread.query.filter_by(thread_id=thread_id).first()
        if thread:
            messages = thread.messages or []
            messages.append({
                "from": "ai_assistant",
                "content": response_content,
                "timestamp": datetime.utcnow().isoformat(),
                "direction": "outbound"
            })
            thread.messages = messages
            thread.last_updated = datetime.utcnow()
            db.session.commit()
