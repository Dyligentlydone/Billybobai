from ..database import db

# Placeholder for SMSNotificationSettings to resolve NameError
# This is a temporary definition until the actual implementation is confirmed
class SMSNotificationSettings(db.Model):
    __tablename__ = 'sms_notification_settings'

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    business_id = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    account_sid = db.Column(db.String(100), nullable=False)
    auth_token = db.Column(db.String(100), nullable=False)
    messaging_service_sid = db.Column(db.String(100), nullable=True)
    webhook_url = db.Column(db.String(255), nullable=False)
    fallback_url = db.Column(db.String(255), nullable=True)
    status_callback = db.Column(db.String(255), nullable=True)
    retry_count = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<SMSNotificationSettings(workflow_id={self.workflow_id}, enabled={self.enabled})>'
