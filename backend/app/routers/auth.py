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

class PasscodeVerifyResponse(BaseModel):
    business_id: str
    passcode: str
    nickname: str = None
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
    client = db.query(ClientPasscode).filter(ClientPasscode.passcode == request.passcode).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid passcode")
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
    business_id: int
    user_id: int

@router.post("/direct-client-create")
def create_direct_client(request: DirectClientAccessRequest, db: Session = Depends(get_db)):
    # Implement your logic for direct client creation
    return {"detail": "Direct client created (mock)"}

@router.get("/direct-clients")
def get_direct_clients(db: Session = Depends(get_db)):
    # Implement your logic to fetch direct clients
    return {"clients": []}

@router.post("/direct-clients")
def post_direct_clients(db: Session = Depends(get_db)):
    # Implement your logic to handle direct client POST
    return {"detail": "Direct client POST handled (mock)"}
