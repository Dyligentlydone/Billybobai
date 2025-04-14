"""
SendGrid integration model.
"""
from sqlalchemy.orm import relationship
from .base import Integration
from ..schemas.integration import IntegrationType

class SendGridIntegration(Integration):
    """Model for SendGrid integration."""
    __mapper_args__ = {
        'polymorphic_identity': IntegrationType.SENDGRID
    }

    def validate_config(self):
        """Validate the integration configuration."""
        required_fields = ['api_key', 'from_email']
        return all(field in self.config for field in required_fields)

    def get_template_id(self, template_type):
        """Get a specific template ID by type."""
        return self.config.get('template_ids', {}).get(template_type)
