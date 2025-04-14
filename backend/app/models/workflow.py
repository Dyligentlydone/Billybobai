"""
This module is deprecated. Import from models.workflow or models.workflow_schemas instead.
This file exists only for backward compatibility.
"""
from models.workflow import Workflow, WorkflowStatus
from models.workflow_schemas import (
    ExecutionStatus,
    NodeExecution,
    WorkflowExecutionSchema as WorkflowExecution,
    WorkflowNode,
    WorkflowEdge
)

# Re-export for backward compatibility
__all__ = [
    'Workflow',
    'WorkflowStatus',
    'ExecutionStatus',
    'NodeExecution',
    'WorkflowExecution',
    'WorkflowNode',
    'WorkflowEdge'
]

from app.database import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List
from pydantic import BaseModel

class Workflow(db.Model):
    __tablename__ = 'workflows'

    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, active, archived
    client_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    nodes = db.Column(JSON, default=[])
    edges = db.Column(JSON, default=[])
    executions = db.Column(JSON, default={})

    def __repr__(self):
        return f'<Workflow {self.name}>'
