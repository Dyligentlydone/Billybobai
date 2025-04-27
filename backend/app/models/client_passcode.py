from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import db

class ClientPasscode(db.Model):
    __tablename__ = 'client_passcodes'

    id = Column(Integer, primary_key=True)
    # Foreign key must match type of businesses.id (Integer)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
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
