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

from sqlalchemy import Column, String, DateTime, JSON
from app.db import db
Base = db.Model
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List
from pydantic import BaseModel
import uuid

class WorkflowStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'

class Workflow(Base):
    __tablename__ = 'workflows'

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    status = Column(String(50), default=WorkflowStatus.DRAFT)
    client_id = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    actions = Column(JSON, default={})
    conditions = Column(JSON, default={})
    nodes = Column(JSON, default=[])
    edges = Column(JSON, default=[])
    executions = Column(JSON, default={})

    def __repr__(self):
        return f'<Workflow {self.name}>'

class WorkflowNode(BaseModel):
    id: str
    type: str
    data: Dict
    position: Dict[str, int]

class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool = False

class WorkflowExecution(BaseModel):
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    node_executions: List[Dict]
