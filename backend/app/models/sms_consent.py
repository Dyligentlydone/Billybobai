from ..db import db
from datetime import datetime

class SMSConsent(db.Model):
    """Tracks SMS opt-in status per phone number and business."""
    __tablename__ = 'sms_consents'

    # Remove the id column and make phone_number + business_id the composite primary key
    phone_number = db.Column(db.String(20), primary_key=True)
    business_id = db.Column(db.String(255), primary_key=True)
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

    def __repr__(self):
        return f"<SMSConsent {self.phone_number} – {self.business_id} – {self.status}>"
