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
    
    # Ensure token is properly formatted
    if not token or len(token) < 10:  # Basic validation
        return {
            "valid": False,
            "error": "Token appears to be invalid or empty",
            "message": "Please check your token format"
        }
        
    # Log token format for debugging (first 5 chars only)
    token_prefix = token[:5] if len(token) >= 5 else token
    print(f"Token validation request with token prefix: {token_prefix}...")
    
    # Accept both old (cal_) and new (eyja) token formats
    valid_prefix = token.startswith("cal_") or token.startswith("eyja")
    if not valid_prefix:
        print(f"Warning: Token doesn't start with expected prefixes (cal_ or eyja)")
        # We'll still try to validate it anyway
    
    try:
        print(f"Attempting to validate Calendly token: {token[:5]}...")
        
        # Define potential API endpoints to try based on token format
        endpoints_to_try = [
            "https://api.calendly.com/v2/users/me",  # Standard v2 API endpoint
            "https://api.calendly.com/users/me",     # Without v2 prefix
            "https://api.calendly.com/api/users/me", # With api prefix
            "https://api.calendly.com/v1/users/me"   # Legacy v1 endpoint
        ]
        
        # If token starts with eyja, prioritize different endpoints
        if token.startswith("eyja"):
            endpoints_to_try = [
                "https://api.calendly.com/users/me",     # Try without v2 first
                "https://api.calendly.com/api/users/me", # Then with api prefix
                "https://api.calendly.com/v2/users/me",  # Then standard v2
                "https://api.calendly.com/v1/users/me"   # Then legacy v1
            ]
            
        # Try different authorization header formats too
        auth_headers_to_try = [
            {"Authorization": f"Bearer {token}"},
            {"Authorization": token}  # Without Bearer prefix
        ]
        
        success = False
        error_messages = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:  # Longer timeout
            # Try each endpoint with each auth header format
            for endpoint in endpoints_to_try:
                for auth_header in auth_headers_to_try:
                    headers = {
                        **auth_header,
                        "Content-Type": "application/json"
                    }
                    
                    try:
                        print(f"Trying endpoint: {endpoint} with auth: {list(auth_header.keys())[0]}")
                        response = await client.get(endpoint, headers=headers)
                        print(f"Calendly API response status: {response.status_code}")
                        
                        # Log response for debugging
                        try:
                            print(f"Calendly API response: {response.text[:500]}...")
                        except:
                            print("Could not print response text")
                        
                        # If successful, extract user data
                        if response.status_code == 200:
                            success = True
                            user_data = response.json()
                            
                            # Try to extract user info from different response formats
                            if "resource" in user_data:
                                # Standard v2 format
                                return {
                                    "valid": True,
                                    "uri": user_data["resource"]["uri"],
                                    "name": user_data["resource"]["name"],
                                    "email": user_data["resource"]["email"],
                                    "message": "Token validated successfully"
                                }
                            elif "data" in user_data and isinstance(user_data["data"], dict):
                                # Alternative format
                                data = user_data["data"]
                                return {
                                    "valid": True,
                                    "uri": data.get("uri") or data.get("id"),
                                    "name": data.get("name") or data.get("display_name"),
                                    "email": data.get("email"),
                                    "message": "Token validated successfully"
                                }
                            else:
                                # Fallback - just use what we have
                                print(f"Found user data in unexpected format: {list(user_data.keys())}")
                                return {
                                    "valid": True,
                                    "message": "Token validated successfully",
                                    "raw_data": user_data
                                }
                    except Exception as e:
                        error_message = f"Error with {endpoint}: {str(e)}"
                        print(error_message)
                        error_messages.append(error_message)
                        continue  # Try next endpoint
        
        # If we got here, all attempts failed
        if error_messages:
            print(f"All validation attempts failed: {error_messages}")
            
        return {
            "valid": False,
            "error": "Failed to validate token with any endpoint",
            "message": "Token validation failed after trying multiple endpoints"
        }
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e} - Status code: {e.response.status_code}")
        error_message = "Invalid token or permission denied"
        try:
            error_data = e.response.json()
            if "message" in error_data:
                error_message = error_data["message"]
        except:
            pass
        
        return {
            "valid": False,
            "error": f"HTTP error {e.response.status_code}",
            "message": error_message
        }
    except httpx.TimeoutException:
        print("Timeout occurred while connecting to Calendly API")
        return {
            "valid": False,
            "error": "Request timed out",
            "message": "Calendly API is not responding"
        }
    except Exception as e:
        print(f"Unexpected error during Calendly validation: {str(e)}")
        return {
            "valid": False,
            "error": str(e),
            "message": "An error occurred while validating your token"
        }
