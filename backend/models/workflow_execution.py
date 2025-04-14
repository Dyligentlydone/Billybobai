from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class ExecutionStatus(enum.Enum):
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class WorkflowExecution(Base):
    __tablename__ = 'workflow_executions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(255), ForeignKey('workflows.id'), nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.IN_PROGRESS)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(String(1000))
    execution_data = Column(JSON)

    # Relationships
    workflow = relationship('Workflow', back_populates='workflow_executions')

    def __repr__(self):
        return f'<WorkflowExecution {self.id} {self.status.value}>'
