from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db
Base = db.Model

class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    workflows = relationship("Workflow", back_populates="business")
    config = relationship("BusinessConfig", back_populates="business", uselist=False)

class BusinessConfig(Base):
    __tablename__ = 'business_configs'

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    business = relationship("Business", back_populates="config")
    
    # Brand voice settings
    tone = Column(String(50), default='professional')  # professional, casual, friendly, etc.
    language = Column(String(10), default='en')  # en, es, fr, etc.
    
    # AI configuration
    ai_settings = Column(JSON, default={})  # temperature, max_tokens, etc.
    custom_instructions = Column(String(2000))  # Additional AI instructions
    
    # Response templates
    greeting_template = Column(String(500))
    fallback_message = Column(String(500))
    
    # Business hours
    business_hours = Column(JSON, default={})  # Format: {"mon": {"start": "09:00", "end": "17:00"}, ...}
    timezone = Column(String(50), default='UTC')
    
    # Integration settings
    calendly_settings = Column(JSON, nullable=True)  # Calendly integration settings
    twilio_settings = Column(JSON, nullable=True)  # Twilio specific settings
