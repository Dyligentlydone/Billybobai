from app.database import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List
from pydantic import BaseModel

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class NodeExecution(BaseModel):
    node_id: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[Dict] = None
    error: Optional[str] = None
    retry_count: int = 0

class WorkflowExecution(BaseModel):
    workflow_id: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Dict
    variables: Dict
    node_executions: Dict[str, NodeExecution]
    error: Optional[str] = None

class WorkflowNode(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict

class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

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
