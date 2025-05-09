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

# Define all models that should be available when importing from app.models
__all__ = [
    'Business', 
    'BusinessConfig',
    'Workflow',
    'WorkflowNode',
    'WorkflowEdge',
    'WorkflowExecution',
    'ClientPasscode',
    'SMSConsent'
]