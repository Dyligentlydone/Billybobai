from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr

class BusinessConfig(BaseModel):
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

class Business(BaseModel):
    id: str
    name: str
    domain: str
    contact_email: EmailStr
    config: BusinessConfig
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
