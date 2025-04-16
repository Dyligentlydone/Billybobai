from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class OptOut(Base):
    __tablename__ = 'opt_outs'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(15), nullable=False)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    opted_out_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reason = Column(String(100))
    
    # Relationships
    business = relationship("Business", back_populates="opt_outs")
    
    __table_args__ = (
        UniqueConstraint('phone_number', 'business_id', name='uq_opt_out_phone_business'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'business_id': self.business_id,
            'opted_out_at': self.opted_out_at.isoformat(),
            'reason': self.reason
        }
