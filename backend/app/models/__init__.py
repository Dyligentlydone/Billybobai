"""
This module is deprecated. Import models from the root models package instead.
This file exists only for backward compatibility.
"""
from models.workflow import Workflow
from models.workflow_execution import WorkflowExecution
from .email import InboundEmail, EmailThread, Attachment
from .business import Business, BusinessConfig

__all__ = [
    'Workflow',
    'WorkflowExecution',
    'InboundEmail',
    'EmailThread',
    'Attachment',
    'Business',
    'BusinessConfig'
]