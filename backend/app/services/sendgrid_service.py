from typing import Dict, List, Optional
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: str
    subject: str
    template_id: Optional[str] = None
    template_data: Optional[Dict] = None
    content: Optional[str] = None
    type: str = "template"  # template, custom, dynamic
    attachments: Optional[List[Dict]] = None

class TemplatePreviewRequest(BaseModel):
    template_id: str
    template_data: Optional[Dict] = None

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

    async def get_templates(self) -> List[Dict]:
        """Fetch all available templates from SendGrid."""
        try:
            response = await self.client.client.templates.get()
            templates = []
            for template in response.templates:
                # Extract variables from template content
                variables = self._extract_template_variables(template)
                
                # Determine template style/category
                style = self._determine_template_style(template)
                
                templates.append({
                    "id": template.id,
                    "name": template.name,
                    "version_id": template.versions[0].id if template.versions else None,
                    "updated_at": template.updated_at,
                    "variables": variables,
                    "style": style
                })
            return templates
        except Exception as e:
            raise Exception(f"Failed to fetch templates: {str(e)}")

    async def preview_template(self, request: TemplatePreviewRequest) -> Dict:
        """Generate a preview of a template with test data."""
        try:
            # Get template details
            response = await self.client.client.templates._(request.template_id).get()
            template = response.template
            
            # Get the active version
            active_version = next((v for v in template.versions if v.active), template.versions[0])
            
            # Extract variables if no test data provided
            if not request.template_data:
                variables = self._extract_template_variables(template)
                request.template_data = self._generate_test_data(variables)
            
            # Generate preview with test data
            preview = await self.client.client.templates._(request.template_id).versions._(active_version.id).generate.post(
                request_body={"template_data": request.template_data}
            )
            
            return {
                "subject": preview.subject,
                "content": preview.html_content,
                "test_data": request.template_data
            }
        except Exception as e:
            raise Exception(f"Failed to generate preview: {str(e)}")

    def _extract_template_variables(self, template) -> List[str]:
        """Extract variables from template content using regex."""
        import re
        variables = set()
        
        # Look for variables in the format {{variable}}
        pattern = r'\{\{([^}]+)\}\}'
        
        # Check all versions
        for version in template.versions:
            if version.html_content:
                matches = re.findall(pattern, version.html_content)
                variables.update(matches)
            
            if version.subject:
                matches = re.findall(pattern, version.subject)
                variables.update(matches)
        
        return sorted(list(variables))

    def _determine_template_style(self, template) -> str:
        """Determine template style/category based on content and metadata."""
        name_lower = template.name.lower()
        
        # Check name for hints
        if any(word in name_lower for word in ['support', 'ticket', 'help']):
            return 'support'
        elif any(word in name_lower for word in ['marketing', 'campaign', 'newsletter']):
            return 'marketing'
        elif any(word in name_lower for word in ['receipt', 'confirm', 'verify']):
            return 'transactional'
        
        # Default to transactional if no clear indicators
        return 'transactional'

    def _generate_test_data(self, variables: List[str]) -> Dict:
        """Generate sample test data for template variables."""
        test_data = {}
        for var in variables:
            # Generate appropriate test data based on variable name
            if 'name' in var.lower():
                test_data[var] = 'John Doe'
            elif 'email' in var.lower():
                test_data[var] = 'john.doe@example.com'
            elif 'date' in var.lower():
                test_data[var] = '2025-03-25'
            elif 'amount' in var.lower() or 'price' in var.lower():
                test_data[var] = '$99.99'
            else:
                test_data[var] = f'Sample {var}'
        return test_data

    def validate_webhook(self, request_data: Dict) -> bool:
        """Validate incoming webhook request from SendGrid."""
        # Add validation logic here
        return True
