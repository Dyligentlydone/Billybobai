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

class WorkflowExecutionSchema(BaseModel):
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
