"""
Twilio integration model.
"""
from sqlalchemy.orm import relationship
from .base import Integration
from ..schemas.integration import IntegrationType

class TwilioIntegration(Integration):
    """Model for Twilio integration."""
    __mapper_args__ = {
        'polymorphic_identity': IntegrationType.TWILIO
    }

    def validate_config(self):
        """Validate the integration configuration."""
        required_fields = ['account_sid', 'auth_token', 'phone_number']
        return all(field in self.config for field in required_fields)

    def get_messaging_service(self):
        """Get the messaging service SID if configured."""
        return self.config.get('messaging_service_sid')
