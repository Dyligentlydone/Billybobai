"""
Calendly integration model.
"""
from sqlalchemy.orm import relationship
from .base import Integration
from ..schemas.integration import IntegrationType

class CalendlyIntegration(Integration):
    """Model for Calendly integration."""
    __mapper_args__ = {
        'polymorphic_identity': IntegrationType.CALENDLY
    }

    def validate_config(self):
        """Validate the integration configuration."""
        required_fields = ['access_token', 'refresh_token', 'organization_url']
        return all(field in self.config for field in required_fields)
