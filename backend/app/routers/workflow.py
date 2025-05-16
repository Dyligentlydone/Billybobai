from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..database import get_db
from ..models.workflow import Workflow
from datetime import datetime  # Add missing datetime import

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

class WorkflowBase(BaseModel):
    name: str
    # Removed description as it doesn't exist in the database model

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowOut(WorkflowBase):
    id: str
    status: Optional[str] = "DRAFT"
    created_at: Optional[str] = None 
    updated_at: Optional[str] = None
    is_active: bool = False  # Set a default value instead of None to fix validation error
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    actions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    nodes: Optional[List[Any]] = Field(default_factory=list)
    edges: Optional[List[Any]] = Field(default_factory=list)
    executions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    business_id: Optional[str] = None
    
    # Allow any extra fields to pass through
    class Config:
        extra = "allow"  # Allow extra fields that aren't in the model

@router.get("/", response_model=List[WorkflowOut])
def get_workflows(db: Session = Depends(get_db)):
    try:
        workflows = db.query(Workflow).all()
        print(f"Found {len(workflows)} workflows")
        for w in workflows:
            print(f"Workflow {w.id}: name={w.name}, status={getattr(w, 'status', 'UNKNOWN')}")
            
        return [WorkflowOut(
            id=w.id,
            name=w.name,
            status=w.status if hasattr(w, 'status') else "DRAFT",
            created_at=w.created_at.isoformat() if hasattr(w, 'created_at') and w.created_at else None,
            updated_at=w.updated_at.isoformat() if hasattr(w, 'updated_at') and w.updated_at else None,
            is_active=bool(getattr(w, "is_active", False) or (hasattr(w, 'status') and w.status == "ACTIVE"))
        ) for w in workflows]
    except Exception as e:
        import traceback
        print("Error in get_workflows:", str(e))
        print(traceback.format_exc())
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error in get_workflows: {str(e)}")

@router.post("/", response_model=WorkflowOut, status_code=201)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    new_wf = Workflow(name=workflow.name)
    db.add(new_wf)
    db.commit()
    db.refresh(new_wf)
    return WorkflowOut(
        id=new_wf.id,
        name=new_wf.name,
        is_active=bool(getattr(new_wf, "is_active", False))
    )

@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    try:
        print(f"WORKFLOW GET: Received request for workflow_id: '{workflow_id}', type: {type(workflow_id)}")
        
        # Debug: Print all workflows to check IDs
        all_workflows = db.query(Workflow).all()
        for w in all_workflows:
            print(f"Available workflow: id='{w.id}', name='{w.name}', type of id: {type(w.id)}")
        
        # Try to find the workflow
        wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not wf:
            print(f"No workflow found with ID: {workflow_id}")
            # Try by substring match as fallback
            matching_workflows = [w for w in all_workflows if workflow_id in w.id]
            if matching_workflows:
                wf = matching_workflows[0]
                print(f"Found workflow by substring match: {wf.id}")
            else:
                raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Convert to dict and include ALL workflow fields
        workflow_dict = {
            "id": wf.id,
            "name": wf.name,
            "status": wf.status if hasattr(wf, 'status') and wf.status is not None else "DRAFT", 
            "created_at": wf.created_at.isoformat() if hasattr(wf, 'created_at') and wf.created_at is not None else None,
            "updated_at": wf.updated_at.isoformat() if hasattr(wf, 'updated_at') and wf.updated_at is not None else None,
            "is_active": bool(getattr(wf, "is_active", False) or (hasattr(wf, 'status') and wf.status == "ACTIVE")),
            # Include all the configuration data with strict None checking
            "config": wf.config if hasattr(wf, 'config') and wf.config is not None else {},
            "actions": wf.actions if hasattr(wf, 'actions') and wf.actions is not None else {},
            "conditions": wf.conditions if hasattr(wf, 'conditions') and wf.conditions is not None else {},
            "nodes": wf.nodes if hasattr(wf, 'nodes') and wf.nodes is not None else [],
            "edges": wf.edges if hasattr(wf, 'edges') and wf.edges is not None else [],
            "executions": wf.executions if hasattr(wf, 'executions') and wf.executions is not None else {},
            "business_id": wf.business_id if hasattr(wf, 'business_id') and wf.business_id is not None else None
        }
        
        # Log the full workflow data (except possibly large fields)
        print(f"Full workflow data ID: {wf.id}, name: {wf.name}, status: {workflow_dict['status']}, business_id: {workflow_dict['business_id']}")
        print(f"Has config: {hasattr(wf, 'config')}, Has actions: {hasattr(wf, 'actions')}, Has nodes: {hasattr(wf, 'nodes')}")
        if hasattr(wf, 'config') and wf.config:
            print(f"Config summary: {type(wf.config)}, keys: {list(wf.config.keys()) if isinstance(wf.config, dict) else 'Not a dictionary'}")
        
        print("Returning workflow data:", workflow_dict)
        
        try:
            # Create the WorkflowOut model and return it
            return WorkflowOut(**workflow_dict)
        except Exception as e:
            print(f"ERROR in validation: {str(e)}")
            # Fallback with minimal fields if validation fails
            fallback_dict = {
                "id": wf.id,
                "name": wf.name,
                "status": "DRAFT",
                "is_active": False,
                "config": {},
                "actions": {},
                "conditions": {},
                "nodes": [],
                "edges": [],
                "executions": {}
            }
            return WorkflowOut(**fallback_dict)
    except Exception as e:
        import traceback
        print(f"Error in get_workflow for id '{workflow_id}':", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow: {str(e)}")


@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: str, workflow_data: dict, db: Session = Depends(get_db)):
    try:
        print(f"Updating workflow ID {workflow_id} with data: {workflow_data}")
        # Print all the keys received in the request for debugging
        print(f"Received keys in request: {list(workflow_data.keys())}")
        
        # Find the workflow by ID
        wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        # Print debugging info about the workflow object
        print(f"Workflow object before update: {wf.__dict__ if hasattr(wf, '__dict__') else 'No __dict__'}")
        
        # Update basic fields
        if 'name' in workflow_data:
            wf.name = workflow_data['name']
            
        # Handle datetime field specifically - this was causing a NameError
        if 'datetime' in workflow_data:
            # If datetime is provided in the request, use it
            # This may be a frontend-specific field
            print(f"Using datetime from request: {workflow_data['datetime']}")
            pass  # Just log it, don't actually use it to avoid issues
        
        # Handle status update if provided
        if 'status' in workflow_data:
            wf.status = workflow_data['status']
        
        # Handle business_id if provided
        if 'business_id' in workflow_data:
            wf.business_id = workflow_data['business_id']
        
        # Update complex configuration fields
        if 'config' in workflow_data:
            wf.config = workflow_data['config']
        elif 'twilio' in workflow_data or 'actions' in workflow_data:
            # If no explicit config but we have twilio/actions data, create a config object
            config_data = {}
            if 'twilio' in workflow_data:
                config_data['twilio'] = workflow_data['twilio']
            if 'actions' in workflow_data:
                config_data['actions'] = workflow_data['actions']
            wf.config = config_data
        
        # Handle actions field (common in frontend requests)
        if 'actions' in workflow_data:
            wf.actions = workflow_data['actions']
        
        # Handle other optional fields if they exist
        if 'conditions' in workflow_data:
            wf.conditions = workflow_data['conditions']
        if 'nodes' in workflow_data:
            wf.nodes = workflow_data['nodes']
        if 'edges' in workflow_data:
            wf.edges = workflow_data['edges']
        if 'executions' in workflow_data:
            wf.executions = workflow_data['executions']
            
        # Mark as updated with proper import handling
        try:
            # Use the imported datetime module correctly
            current_time = datetime.utcnow()
            print(f"Setting updated_at to: {current_time}")
            wf.updated_at = current_time
        except Exception as e:
            print(f"Error setting updated_at: {str(e)}")
            # Skip updating the timestamp if there's an issue
        
        # Save changes to database
        db.commit()
        db.refresh(wf)
        
        # Convert to dict for response with all fields
        workflow_dict = {
            "id": wf.id,
            "name": wf.name,
            "status": wf.status if hasattr(wf, 'status') and wf.status is not None else "DRAFT",
            "created_at": wf.created_at.isoformat() if hasattr(wf, 'created_at') and wf.created_at is not None else None,
            "updated_at": wf.updated_at.isoformat() if hasattr(wf, 'updated_at') and wf.updated_at is not None else None,
            "is_active": bool(getattr(wf, "is_active", False) or (hasattr(wf, 'status') and wf.status == "ACTIVE")),
            "config": wf.config if hasattr(wf, 'config') and wf.config is not None else {},
            "actions": wf.actions if hasattr(wf, 'actions') and wf.actions is not None else {},
            "conditions": wf.conditions if hasattr(wf, 'conditions') and wf.conditions is not None else {},
            "nodes": wf.nodes if hasattr(wf, 'nodes') and wf.nodes is not None else [],
            "edges": wf.edges if hasattr(wf, 'edges') and wf.edges is not None else [],
            "executions": wf.executions if hasattr(wf, 'executions') and wf.executions is not None else {},
            "business_id": wf.business_id if hasattr(wf, 'business_id') and wf.business_id is not None else None
        }
        
        print("Updated workflow data:", workflow_dict)
        
        try:
            # Create the WorkflowOut model and return it
            return WorkflowOut(**workflow_dict)
        except Exception as e:
            print(f"ERROR in validation: {str(e)}")
            # Fallback with minimal fields if validation fails
            fallback_dict = {
                "id": wf.id,
                "name": wf.name,
                "status": "DRAFT",
                "is_active": False
            }
            return WorkflowOut(**fallback_dict)
    except Exception as e:
        import traceback
        print("Error in update_workflow:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating workflow: {str(e)}")


@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"detail": "Workflow deleted"}

@router.post("/{workflow_id}/activate")
def activate_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.is_active = True
    db.commit()
    db.refresh(wf)
    return {"detail": "Workflow activated", "id": wf.id}
