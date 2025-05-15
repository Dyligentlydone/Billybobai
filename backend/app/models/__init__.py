"""
Models package for the application.
"""
import os
import sys
import importlib
import logging

logger = logging.getLogger(__name__)

# Only import db from app.db
from app.db import db

# Define all expected models
MODEL_IMPORTS = {
    "Business": "app.models.business",
    "BusinessConfig": "app.models.business",
    "Workflow": "app.models.workflow",
    "WorkflowNode": "app.models.workflow",
    "WorkflowEdge": "app.models.workflow",
    "WorkflowExecution": "app.models.workflow",
    "ClientPasscode": "app.models.client_passcode",
    "SMSConsent": "app.models.sms_consent",
    "User": "app.models.user",
    "APIIntegration": "app.models.api_integration",
}

# Import models with error handling
def import_model(model_name, module_path):
    try:
        module = importlib.import_module(module_path)
        return getattr(module, model_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"Could not import {model_name} from {module_path}: {str(e)}")
        logger.warning(f"Creating placeholder for {model_name}")
        # Return a placeholder class to prevent import errors
        return type(model_name, (), {
            "__doc__": f"Placeholder for {model_name} model to prevent import errors.",
            "id": None,
            "__tablename__": model_name.lower() + 's',
        })

# Import models
try:
    from app.models.business import Business, BusinessConfig
    from app.models.workflow import Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution
    from app.models.client_passcode import ClientPasscode
    from app.models.sms_consent import SMSConsent
    from app.models.user import User
    from app.models.api_integration import APIIntegration
except ImportError as e:
    logger.warning(f"Error importing models: {str(e)}")
    logger.warning("Fallback to dynamic imports")
    
    # Import models dynamically
    for model_name, module_path in MODEL_IMPORTS.items():
        globals()[model_name] = import_model(model_name, module_path)

# Create a Message class if it doesn't exist but is imported somewhere
class Message:
    """Placeholder for Message model to prevent import errors."""
    __tablename__ = 'messages'
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