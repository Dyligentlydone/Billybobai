from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Business(Base):
    __tablename__ = 'businesses'

    id = Column(String(255), primary_key=True)  # Using String to match actual database schema
    name = Column(String, nullable=False)
    description = Column(String(1000), nullable=True)
    domain = Column(String(255), nullable=False, default="example.com")
    config = relationship("BusinessConfig", back_populates="business", uselist=False)
    passcodes = relationship("ClientPasscode", back_populates="business", cascade="all, delete-orphan")

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

class ClientPasscode(Base):
    __tablename__ = 'client_passcodes'

    id = Column(Integer, primary_key=True)
    business_id = Column(String(255), ForeignKey('businesses.id'), nullable=False)
    passcode = Column(String(5), nullable=False)  # 5-digit passcode
    permissions = Column(JSON, nullable=False)  # Store permissions structure as JSON
    
    business = relationship("Business", back_populates="passcodes")
    
    def to_dict(self):
        return {
            "id": self.id,
            "business_id": self.business_id,
            "passcode": self.passcode,
            "permissions": self.permissions
        }
