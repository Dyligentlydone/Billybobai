from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models.client_passcode import ClientPasscode
from ..models.business import Business

router = APIRouter(prefix="/api/clients", tags=["clients"])

class ClientBase(BaseModel):
    business_id: str

class ClientCreate(ClientBase):
    passcode: str
    nickname: str = None

class ClientOut(BaseModel):
    id: int
    business_id: str
    passcode: str
    nickname: str = None
    permissions: dict

@router.get("/")
def get_clients(business_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ClientPasscode)
    if business_id:
        query = query.filter(ClientPasscode.business_id == business_id)
    clients = query.all()
    return {"clients": [c.to_dict() for c in clients]}
@router.post("/", response_model=ClientOut, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Create default permissions if not provided
    default_permissions = {
        "navigation": {
            "workflows": True,
            "analytics": True,
            "settings": False,
            "api_access": False,
            "dashboard": True,
            "clients": False,
            "voice_setup": False
        },
        "analytics": {
            "sms": {
                "recent_conversations": True,
                "response_time": True,
                "message_volume": True,
                "success_rate": True,
                "cost_per_message": True,
                "ai_usage": True
            },
            "voice": {
                "call_duration": True,
                "call_volume": True,
                "success_rate": True,
                "cost_per_call": True
            },
            "email": {
                "delivery_rate": True,
                "open_rate": True,
                "response_rate": True,
                "cost_per_email": True
            }
        }
    }
    
    new_client = ClientPasscode(
        business_id=client.business_id,
        passcode=client.passcode,
        nickname=client.nickname,
        permissions=default_permissions
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return ClientOut(
        id=new_client.id,
        business_id=new_client.business_id,
        passcode=new_client.passcode,
        nickname=new_client.nickname,
        permissions=new_client.permissions
    )

@router.put("/{client_id}/permissions")
def update_client_permissions(client_id: int, permissions: dict, db: Session = Depends(get_db)):
    client = db.query(ClientPasscode).filter(ClientPasscode.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.permissions = permissions
    db.commit()
    db.refresh(client)
    return {"detail": "Permissions updated", "id": client.id}
