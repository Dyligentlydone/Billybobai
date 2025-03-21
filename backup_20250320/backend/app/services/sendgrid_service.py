from typing import Dict, List, Optional
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Template
from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: str
    subject: str
    template_id: Optional[str] = None
    template_data: Optional[Dict] = None
    content: Optional[str] = None
    type: str = "template"  # template, custom, dynamic
    attachments: Optional[List[Dict]] = None

class SendGridService:
    def __init__(self):
        self.client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL')

    async def send_email(self, request: EmailRequest) -> Dict:
        """Send email via SendGrid based on type (template, custom, or dynamic)."""
        try:
            if request.type == "template":
                return await self._send_template_email(request)
            elif request.type == "custom":
                return await self._send_custom_email(request)
            elif request.type == "dynamic":
                return await self._send_dynamic_email(request)
            else:
                raise ValueError(f"Unsupported email type: {request.type}")
        except Exception as e:
            raise Exception(f"SendGrid error: {str(e)}")

    async def _send_template_email(self, request: EmailRequest) -> Dict:
        """Send template-based email."""
        if not request.template_id:
            raise ValueError("Template ID is required for template emails")

        mail = Mail(
            from_email=self.from_email,
            to_emails=request.to,
            subject=request.subject
        )
        mail.template_id = request.template_id
        
        if request.template_data:
            mail.dynamic_template_data = request.template_data

        if request.attachments:
            for attachment in request.attachments:
                mail.add_attachment(attachment)

        response = await self.client.send(mail)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "type": "template"
        }

    async def _send_custom_email(self, request: EmailRequest) -> Dict:
        """Send custom email with HTML content."""
        if not request.content:
            raise ValueError("Content is required for custom emails")

        mail = Mail(
            from_email=self.from_email,
            to_emails=request.to,
            subject=request.subject,
            html_content=request.content
        )

        if request.attachments:
            for attachment in request.attachments:
                mail.add_attachment(attachment)

        response = await self.client.send(mail)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "type": "custom"
        }

    async def _send_dynamic_email(self, request: EmailRequest) -> Dict:
        """Send dynamic email with personalization."""
        if not request.template_id or not request.template_data:
            raise ValueError("Template ID and data required for dynamic emails")

        mail = Mail(
            from_email=self.from_email,
            to_emails=request.to,
            subject=request.subject
        )
        mail.template_id = request.template_id
        
        # Add personalization data
        personalization = mail.get_personalization()[0]
        for key, value in request.template_data.items():
            personalization.add_dynamic_template_data({key: value})

        if request.attachments:
            for attachment in request.attachments:
                mail.add_attachment(attachment)

        response = await self.client.send(mail)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "type": "dynamic"
        }

    def validate_webhook(self, request_data: Dict) -> bool:
        """Validate incoming webhook request from SendGrid."""
        # Add validation logic here
        return True
