from ..db import db
from datetime import datetime
from sqlalchemy.schema import Sequence

class SMSConsent(db.Model):
    """Tracks SMS opt-in status per phone number and business."""
    __tablename__ = 'sms_consents'

    # Add back the ID column with sequence to auto-generate values
    id = db.Column(db.Integer, Sequence('sms_consent_id_seq'), primary_key=True, nullable=False)
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
