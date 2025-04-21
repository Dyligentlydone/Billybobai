"""
This module defines the Workflow model and related schemas.
"""
from sqlalchemy import Column, String, DateTime, JSON
from app.database import db
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List, Any
from pydantic import BaseModel
import uuid

class WorkflowStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'

class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Workflow(db.Model):
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

class NodeExecution(BaseModel):
    node_id: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[Any] = None

class WorkflowExecution(BaseModel):
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    node_executions: List[Dict]
