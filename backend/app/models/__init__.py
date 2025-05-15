"""
Models package for the application.
"""
# Only import db from app.db
from app.db import db

# Import models
from app.models.business import Business, BusinessConfig
from app.models.workflow import Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution
from app.models.client_passcode import ClientPasscode
from app.models.sms_consent import SMSConsent
from app.models.user import User

# Create a Message class if it doesn't exist but is imported somewhere
class Message:
    """Placeholder for Message model to prevent import errors."""
    id = None
    business_id = None
    client_id = None
    content = None
    created_at = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Define all models that should be available when importing from app.models
__all__ = [
    'Business', 
    'BusinessConfig',
    'Workflow',
    'WorkflowNode',
    'WorkflowEdge',
    'WorkflowExecution',
    'ClientPasscode',
    'Message',
    'SMSConsent'
]