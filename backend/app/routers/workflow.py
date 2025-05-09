from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models.workflow import Workflow

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

class WorkflowBase(BaseModel):
    name: str
    description: str = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowOut(WorkflowBase):
    id: int
    is_active: bool = None

@router.get("/", response_model=List[WorkflowOut])
def get_workflows(db: Session = Depends(get_db)):
    workflows = db.query(Workflow).all()
    return [WorkflowOut(
        id=w.id,
        name=w.name,
        description=w.description,
        is_active=getattr(w, "is_active", None)
    ) for w in workflows]

@router.post("/", response_model=WorkflowOut, status_code=201)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    new_wf = Workflow(name=workflow.name, description=workflow.description)
    db.add(new_wf)
    db.commit()
    db.refresh(new_wf)
    return WorkflowOut(
        id=new_wf.id,
        name=new_wf.name,
        description=new_wf.description,
        is_active=getattr(new_wf, "is_active", None)
    )

@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowOut(
        id=wf.id,
        name=wf.name,
        description=wf.description,
        is_active=getattr(wf, "is_active", None)
    )

@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: int, workflow: WorkflowCreate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.name = workflow.name
    wf.description = workflow.description
    db.commit()
    db.refresh(wf)
    return WorkflowOut(
        id=wf.id,
        name=wf.name,
        description=wf.description,
        is_active=getattr(wf, "is_active", None)
    )

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"detail": "Workflow deleted"}

@router.post("/{workflow_id}/activate")
def activate_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.is_active = True
    db.commit()
    db.refresh(wf)
    return {"detail": "Workflow activated", "id": wf.id}
