from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models.client_passcode import ClientPasscode
from ..models.business import Business

router = APIRouter(prefix="/api/clients", tags=["clients"])

class ClientBase(BaseModel):
    name: str
    business_id: str
    email: str = None

class ClientCreate(ClientBase):
    pass

class ClientOut(ClientBase):
    id: int
    permissions: dict = None

@router.get("/", response_model=List[ClientOut])
def get_clients(business_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ClientPasscode)
    if business_id:
        query = query.filter(ClientPasscode.business_id == business_id)
    clients = query.all()
    return [ClientOut(
        id=c.id,
        name=getattr(c, 'name', None),
        business_id=c.business_id,
        email=getattr(c, 'email', None),
        permissions=getattr(c, 'permissions', None)
    ) for c in clients]

@router.post("/", response_model=ClientOut, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    new_client = ClientPasscode(
        name=client.name,
        business_id=client.business_id,
        email=client.email
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return ClientOut(
        id=new_client.id,
        name=new_client.name,
        business_id=new_client.business_id,
        email=new_client.email,
        permissions=getattr(new_client, 'permissions', None)
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
