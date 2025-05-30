from datetime import datetime
import logging
from typing import Dict, Any, Optional

# Import directly from services to avoid circular imports
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.workflow import Workflow

logger = logging.getLogger(__name__)

async def verify_appointment_with_service(business_id: str, search_date: datetime) -> Dict[str, Any]:
    """
    Directly call the Calendly service to verify if an appointment exists
    
    Args:
        business_id: The business/workflow ID
        search_date: The date/time to verify
        
    Returns:
        Dict containing verification results
    """
    try:
        # Import here to avoid circular imports
        from ..services.calendly import CalendlyService
        from ..schemas.calendly import CalendlyConfig
        
        logger.info(f"Verifying appointment for business {business_id} at {search_date}")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get the workflow
            workflow = db.query(Workflow).filter(Workflow.id == business_id).first()
            if not workflow:
                logger.error(f"Workflow not found for business ID: {business_id}")
                return {
                    "success": False,
                    "error": "Workflow not found",
                    "message": f"No workflow found for business ID: {business_id}"
                }
            
            # Check if Calendly is configured
            actions = workflow.actions
            calendly_config = actions.get('calendly', {})
            if not calendly_config.get('enabled'):
                logger.error(f"Calendly not enabled for business ID: {business_id}")
                return {
                    "success": False,
                    "error": "Calendly not enabled",
                    "message": "Calendly integration is not enabled for this workflow"
                }
                
            # Create Calendly service
            calendly_service = CalendlyService(CalendlyConfig(
                enabled=True,
                access_token=calendly_config.get('access_token', ''),
                user_uri=calendly_config.get('user_uri'),
                default_event_type=calendly_config.get('default_event_type', ''),
                booking_window_days=calendly_config.get('booking_window_days', 14),
                min_notice_hours=calendly_config.get('min_notice_hours', 1),
            ))
            
            # Call the verification method directly
            verification_result = await calendly_service.verify_appointment(search_date)
            
            logger.info(f"Successfully verified appointment: {verification_result}")
            return {
                "success": True,
                "verification": verification_result
            }
            
        finally:
            db.close()
            
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
    logger.info(f"Formatting appointment response: {verification_result}")
    
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
