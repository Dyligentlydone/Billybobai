from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from ..database import get_db
from pydantic import BaseModel
import httpx
from typing import Dict, Optional, Any

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

class AIAnalyzeRequest(BaseModel):
    text: str
    
class CalendlyTokenRequest(BaseModel):
    access_token: str

@router.post("/ai/analyze")
def ai_analyze(request: AIAnalyzeRequest, db: Session = Depends(get_db)):
    # Implement AI analysis logic
    return {"result": "AI analysis result (mock)"}

@router.post("/twilio/send")
def twilio_send(request: Request, db: Session = Depends(get_db)):
    # Implement Twilio send logic
    return {"detail": "Twilio message sent (mock)"}

@router.post("/sendgrid/send")
def sendgrid_send(request: Request, db: Session = Depends(get_db)):
    # Implement Sendgrid send logic
    return {"detail": "Sendgrid message sent (mock)"}

@router.get("/sendgrid/templates")
def get_sendgrid_templates(db: Session = Depends(get_db)):
    # Implement logic to fetch Sendgrid templates
    return {"templates": []}

@router.post("/sendgrid/templates/preview")
def preview_sendgrid_template(request: Request, db: Session = Depends(get_db)):
    # Implement logic to preview Sendgrid template
    return {"preview": "Sendgrid template preview (mock)"}

@router.post("/zendesk/ticket")
def create_zendesk_ticket(request: Request, db: Session = Depends(get_db)):
    # Implement Zendesk ticket creation
    return {"detail": "Zendesk ticket created (mock)"}

@router.put("/zendesk/ticket/{ticket_id}")
def update_zendesk_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    # Implement Zendesk ticket update
    return {"detail": f"Zendesk ticket {ticket_id} updated (mock)"}

@router.post("/zendesk/ticket/{ticket_id}/comment")
def comment_zendesk_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    # Implement Zendesk ticket comment
    return {"detail": f"Comment added to Zendesk ticket {ticket_id} (mock)"}

@router.post("/config/email")
def config_email(request: Request, db: Session = Depends(get_db)):
    # Implement email config logic
    return {"detail": "Email config set (mock)"}

@router.post("/calendly/validate-token")
async def validate_calendly_token(request: CalendlyTokenRequest, db: Session = Depends(get_db)):
    """Validate Calendly token and return user information"""
    token = request.access_token
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.calendly.com/v2/users/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            user_data = response.json()
            
            # Extract user info
            return {
                "valid": True,
                "user_uri": user_data["resource"]["uri"],
                "name": user_data["resource"]["name"],
                "email": user_data["resource"]["email"],
                "message": "Token validated successfully"
            }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Invalid or expired token"
        }
