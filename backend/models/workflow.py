from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
from .base import Base

class WorkflowStatus(enum.Enum):
    ACTIVE = 'active'
    DRAFT = 'draft'
    ARCHIVED = 'archived'

class Workflow(Base):
    __tablename__ = 'workflows'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    nodes = Column(JSON)
    edges = Column(JSON)
    variables = Column(JSON)
    executions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # New fields we'll add in migration
    business_id = Column(String(255), ForeignKey('businesses.id'))
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)

    # Relationships
    business = relationship('Business', back_populates='workflows')
    messages = relationship('Message', back_populates='workflow')
    workflow_executions = relationship('WorkflowExecution', back_populates='workflow')

    def __repr__(self):
        return f'<Workflow {self.name}>'
