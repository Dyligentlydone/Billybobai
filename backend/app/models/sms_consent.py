from ..db import db
from datetime import datetime
import time
import random

class SMSConsent(db.Model):
    """Tracks SMS opt-in status per phone number and business."""
    __tablename__ = 'sms_consents'

    # Use a manually generated ID instead of a sequence
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    business_id = db.Column(db.String(255), nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        default='PENDING',  # PENDING, CONFIRMED, DECLINED
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Make sure we have the unique constraint
    __table_args__ = (
        db.UniqueConstraint('phone_number', 'business_id', name='uq_sms_consent_phone_business'),
    )

    def __repr__(self):
        return f"<SMSConsent {self.phone_number} – {self.business_id} – {self.status}>"
        
    # Add a method to generate a unique ID before inserting
    def __init__(self, **kwargs):
        # Generate a unique ID based on timestamp and random number
        if 'id' not in kwargs:
            kwargs['id'] = int(time.time() * 1000) + random.randint(1, 999)
        super(SMSConsent, self).__init__(**kwargs)
