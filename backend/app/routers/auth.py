from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.client_passcode import ClientPasscode
from app.models.business import Business
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Pydantic models for request/response
from fastapi import status

class PasscodeVerifyRequest(BaseModel):
    passcode: str

from typing import Optional

class PasscodeVerifyResponse(BaseModel):
    business_id: str
    passcode: str
    nickname: Optional[str] = None
    permissions: dict

class PasscodeCreate(BaseModel):
    code: str
    business_id: int
    user_id: int

class PasscodeResponse(BaseModel):
    id: int
    code: str
    business_id: int
    user_id: int

@router.get("/passcodes", response_model=List[PasscodeResponse])
def get_passcodes(db: Session = Depends(get_db)):
    passcodes = db.query(ClientPasscode).all()
    return [PasscodeResponse(
        id=p.id, code=p.code, business_id=p.business_id, user_id=p.user_id
    ) for p in passcodes]

# Add debug imports
import logging
logger = logging.getLogger("app.auth")

@router.post("/passcodes/create", response_model=PasscodeResponse)
def create_passcode(passcode: PasscodeCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new passcode: {passcode}")
    new_passcode = ClientPasscode(**passcode.dict())
    db.add(new_passcode)
    db.commit()
    db.refresh(new_passcode)
    return PasscodeResponse(
        id=new_passcode.id, code=new_passcode.code, business_id=new_passcode.business_id, user_id=new_passcode.user_id
    )

@router.post("/passcodes", response_model=PasscodeVerifyResponse)
def legacy_verify_passcode(request: PasscodeVerifyRequest, db: Session = Depends(get_db)):
    """Legacy endpoint to handle old frontend requests that still use /auth/passcodes
    This redirects to the new /auth/passcodes/verify logic."""
    logger.info(f"Legacy passcode verification request received: {request.passcode[:2]}***")
    return verify_passcode(request, db)

@router.post("/passcodes/verify", response_model=PasscodeVerifyResponse)
def verify_passcode(request: PasscodeVerifyRequest, db: Session = Depends(get_db)):
    logger.info(f"Verifying passcode: {request.passcode[:2]}*** (length: {len(request.passcode)})")
    
    # Debug: List all passcodes in the database
    all_passcodes = db.query(ClientPasscode).all()
    logger.info(f"Found {len(all_passcodes)} passcodes in database")
    for p in all_passcodes:
        logger.info(f"DB Passcode: {p.passcode[:2]}*** (length: {len(p.passcode)}) for business_id: {p.business_id}")
    
    # Try to find the client with this passcode
    client = db.query(ClientPasscode).filter(ClientPasscode.passcode == request.passcode).first()
    
    if not client:
        logger.error(f"No client found with passcode: {request.passcode[:2]}***")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid passcode")
    
    logger.info(f"Client found: business_id={client.business_id}, nickname={client.nickname}")
    return PasscodeVerifyResponse(
        business_id=client.business_id,
        passcode=client.passcode,
        nickname=client.nickname,
        permissions=client.permissions
    )

@router.delete("/passcodes/{passcode_id}")
def delete_passcode(passcode_id: int, db: Session = Depends(get_db)):
    passcode = db.query(ClientPasscode).filter_by(id=passcode_id).first()
    if not passcode:
        raise HTTPException(status_code=404, detail="Passcode not found")
    db.delete(passcode)
    db.commit()
    return {"detail": "Passcode deleted"}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: int

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=request.username).first()
    if not user or not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Replace this with your actual JWT logic
    token = f"mock-token-for-{user.id}"
    return LoginResponse(token=token, user_id=user.id)

class DirectClientAccessRequest(BaseModel):
    business_id: str
    passcode: str
    nickname: str = None

@router.post("/direct-client-create")
def create_direct_client(request: DirectClientAccessRequest, db: Session = Depends(get_db)):
    logger.info(f"Creating direct client with business_id={request.business_id}, passcode={request.passcode[:2]}***")
    
    # Create default permissions
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
    
    try:
        # Create new client passcode
        new_client = ClientPasscode(
            business_id=request.business_id,
            passcode=request.passcode,
            nickname=request.nickname,
            permissions=default_permissions
        )
        
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        
        logger.info(f"Successfully created client with id={new_client.id}")
        
        return {
            "id": new_client.id,
            "business_id": new_client.business_id,
            "passcode": new_client.passcode,
            "nickname": new_client.nickname,
            "permissions": new_client.permissions
        }
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Could not create client: {str(e)}")


@router.get("/direct-clients")
def get_direct_clients(db: Session = Depends(get_db)):
    # Implement your logic to fetch direct clients
    return {"clients": []}

@router.post("/direct-clients")
def post_direct_clients(db: Session = Depends(get_db)):
    # Implement your logic to handle direct client POST
    return {"detail": "Direct client POST handled (mock)"}
