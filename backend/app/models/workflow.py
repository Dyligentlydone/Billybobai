"""
This module defines the Workflow model and related schemas.
"""
from app.db import db
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List, Any
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

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default=WorkflowStatus.DRAFT)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))  
    business = db.relationship("Business", back_populates="workflows")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    actions = db.Column(db.JSON, default={})
    conditions = db.Column(db.JSON, default={})
    nodes = db.Column(db.JSON, default=[])
    edges = db.Column(db.JSON, default=[])
    executions = db.Column(db.JSON, default={})
    config = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Workflow {self.name}>'

class WorkflowNode(db.Model):
    __tablename__ = 'workflow_nodes'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String(255), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    position = db.Column(db.JSON, nullable=False)

class WorkflowEdge(db.Model):
    __tablename__ = 'workflow_edges'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = db.Column(db.String(255), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    animated = db.Column(db.Boolean, default=False)

class NodeExecution(db.Model):
    __tablename__ = 'node_executions'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    output = db.Column(db.JSON, nullable=True)

class WorkflowExecution(db.Model):
    __tablename__ = 'workflow_executions'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    node_executions = db.Column(db.JSON, nullable=False)
