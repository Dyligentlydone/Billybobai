import httpx
from datetime import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def verify_appointment(business_id: str, search_date: datetime) -> Dict[str, Any]:
    """
    Call the Calendly verification API to check if an appointment exists
    
    Args:
        business_id: The business/workflow ID
        search_date: The date/time to verify
        
    Returns:
        Dict containing verification results
    """
    try:
        # Use relative URL for internal API calls
        base_url = "http://localhost:8000"  # For local development
        
        # In production, this might come from config
        # In a container environment, this should be the service name
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/integrations/calendly/verify-appointment",
                json={
                    "business_id": business_id,
                    "search_date": search_date.isoformat()
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                verification = response.json()
                logger.info(f"Successfully verified appointment: {verification}")
                return verification
            else:
                logger.error(f"Failed to verify appointment: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "message": response.text
                }
    except Exception as e:
        logger.error(f"Exception in verify_appointment: {str(e)}")
        return {
            "success": False,
            "error": "Internal Error",
            "message": str(e)
        }

def format_appointment_response(verification_result: Dict[str, Any]) -> str:
    """
    Format the appointment verification result into a human-readable response
    
    Args:
        verification_result: The result from the verification API
        
    Returns:
        A formatted string response
    """
    if not verification_result.get("success", False):
        return "I'm sorry, I couldn't verify your appointment due to a technical issue."
    
    verification = verification_result.get("verification", {})
    
    if verification.get("exists", False):
        # Appointment exists
        details = verification.get("details", {})
        start_time = details.get("start_time")
        
        if start_time:
            try:
                dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%A, %B %d at %I:%M %p")
                return f"Yes, I can confirm your appointment for {formatted_time} is still scheduled."
            except:
                return "Yes, your appointment is confirmed. However, I couldn't format the time correctly."
        else:
            return "Yes, your appointment is confirmed."
    else:
        # No appointment found
        closest_time = verification.get("closest_time")
        available_slots = verification.get("available_slots", [])
        
        if closest_time:
            try:
                dt = datetime.fromisoformat(closest_time.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%A, %B %d at %I:%M %p")
                return f"I don't see an appointment at that time, but you do have one scheduled for {formatted_time}."
            except:
                return "I don't see an appointment at that time, but you do have another appointment scheduled."
        elif available_slots:
            # Format up to 3 available slots
            slot_times = []
            for i, slot in enumerate(available_slots[:3]):
                try:
                    dt = datetime.fromisoformat(slot.get("start_time").replace("Z", "+00:00"))
                    slot_times.append(dt.strftime("%I:%M %p"))
                except:
                    continue
                    
            if slot_times:
                slot_str = ", ".join(slot_times)
                return f"I don't see any appointments scheduled. Available slots include: {slot_str}."
            
        return "I don't see any appointments scheduled for that time."
