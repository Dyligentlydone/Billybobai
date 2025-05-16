from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .webhooks import sms_webhook  # Import the existing SMS webhook handler

router = APIRouter(prefix="/api/sms", tags=["sms"])

@router.api_route("/webhook/{business_id}", methods=["GET", "POST"])
async def sms_webhook_handler(business_id: str, request: Request, db: Session = Depends(get_db)):
    """
    SMS webhook handler that matches the URL format expected by Twilio:
    https://api.dyligent.xyz/api/sms/webhook/11111
    
    This redirects to the main SMS webhook handler in the webhooks router.
    """
    print(f"SMS webhook received at /api/sms/webhook/{business_id}")
    # Simply forward to the existing webhook handler
    return await sms_webhook(business_id, request, db)
