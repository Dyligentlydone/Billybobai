"""
Pydantic schemas for integration models.
"""
from datetime import datetime
from typing import Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field

class IntegrationType(str, Enum):
    """Types of supported integrations."""
    CALENDLY = "calendly"
    TWILIO = "twilio"
    SENDGRID = "sendgrid"
    OPENAI = "openai"

class IntegrationStatus(str, Enum):
    """Status of an integration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

class BaseIntegrationSchema(BaseModel):
    """Base schema for all integrations."""
    name: str
    type: IntegrationType
    status: IntegrationStatus = IntegrationStatus.PENDING
    config: Dict
    metadata: Dict = {}
    last_used: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class CalendlyConfigSchema(BaseModel):
    """Schema for Calendly integration config."""
    access_token: str
    refresh_token: str
    organization_url: str
    webhook_signing_key: Optional[str] = None
    user_uri: Optional[str] = None

class TwilioConfigSchema(BaseModel):
    """Schema for Twilio integration config."""
    account_sid: str
    auth_token: str
    phone_number: str
    messaging_service_sid: Optional[str] = None
    webhook_url: Optional[str] = None

class SendGridConfigSchema(BaseModel):
    """Schema for SendGrid integration config."""
    api_key: str
    from_email: str
    inbound_domain: Optional[str] = None
    webhook_key: Optional[str] = None
    template_ids: Dict[str, str] = {}

class OpenAIConfigSchema(BaseModel):
    """Schema for OpenAI integration config."""
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7
    system_prompt: Optional[str] = None
