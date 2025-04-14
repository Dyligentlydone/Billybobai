"""
Pydantic schemas for business-related models.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr

class BusinessConfigSchema(BaseModel):
    """Schema for business configuration."""
    name: str
    domain: str
    email_config: Dict = {
        "sendgrid": {
            "api_key": str,
            "from_email": EmailStr,
            "inbound_domain": Optional[str]
        },
        "openai": {
            "api_key": str
        }
    }
    brand_voice: Dict = {
        "voiceType": str,
        "greetings": List[str],
        "wordsToAvoid": List[str]
    }
    templates: Dict = {
        "support": Dict,
        "marketing": Dict,
        "transactional": Dict
    }
    active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True

class BusinessSchema(BaseModel):
    """Schema for business entity."""
    id: str
    name: str
    domain: str
    status: str
    config: BusinessConfigSchema
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
