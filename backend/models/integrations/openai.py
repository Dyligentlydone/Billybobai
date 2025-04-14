"""
OpenAI integration model.
"""
from sqlalchemy.orm import relationship
from .base import Integration
from ..schemas.integration import IntegrationType

class OpenAIIntegration(Integration):
    """Model for OpenAI integration."""
    __mapper_args__ = {
        'polymorphic_identity': IntegrationType.OPENAI
    }

    def validate_config(self):
        """Validate the integration configuration."""
        required_fields = ['api_key', 'model']
        return all(field in self.config for field in required_fields)

    def get_model_settings(self):
        """Get the model settings."""
        return {
            'model': self.config.get('model', 'gpt-4'),
            'max_tokens': self.config.get('max_tokens', 2000),
            'temperature': self.config.get('temperature', 0.7)
        }
