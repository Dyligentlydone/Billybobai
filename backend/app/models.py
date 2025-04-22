from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True)  # Changed back to Integer for consistency
    name = Column(String, nullable=False)
    description = Column(String(1000), nullable=True)
    domain = Column(String(255), nullable=False)
    config = relationship("BusinessConfig", back_populates="business", uselist=False)

class BusinessConfig(Base):
    __tablename__ = 'business_configs'

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    business = relationship("Business", back_populates="config")
    
    # Store Calendly configuration as JSON
    calendly_settings = Column(JSON, nullable=True)
    
    # Store other service configurations
    twilio_settings = Column(JSON, nullable=True)
    openai_settings = Column(JSON, nullable=True)
    zendesk_settings = Column(JSON, nullable=True)
