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
        import traceback
        
        logger.info(f"[CALENDLY DEBUG] Verifying appointment for business {business_id} at {search_date}")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get the workflow
            workflow = db.query(Workflow).filter(Workflow.id == business_id).first()
            if not workflow:
                logger.error(f"[CALENDLY DEBUG] Workflow not found for business ID: {business_id}")
                return {
                    "success": False,
                    "error": "Workflow not found",
                    "message": f"No workflow found for business ID: {business_id}"
                }
            
            # Dump the whole workflow for debugging
            logger.info(f"[CALENDLY DEBUG] Workflow found: {workflow.id}")
            
            # Check if Calendly is configured
            actions = workflow.actions if workflow.actions else {}
            logger.info(f"[CALENDLY DEBUG] Workflow actions keys: {list(actions.keys())}")
            
            calendly_config = actions.get('calendly', {})
            logger.info(f"[CALENDLY DEBUG] Calendly config in workflow: {calendly_config}")
            
            # Force enable for testing if needed
            if not calendly_config:
                logger.warning(f"[CALENDLY DEBUG] No Calendly config found, creating default for testing")
                calendly_config = {
                    'enabled': True
                }
            
            if not calendly_config.get('enabled'):
                logger.error(f"[CALENDLY DEBUG] Calendly not enabled for business ID: {business_id}")
                return {
                    "success": False,
                    "error": "Calendly not enabled",
                    "message": "Calendly integration is not enabled for this workflow"
                }
            
            # Log token preview for debugging
            token = calendly_config.get('access_token', '')
            if not token:
                logger.error(f"[CALENDLY DEBUG] No Calendly access token found in config")
                return {
                    "success": False,
                    "error": "No Calendly token",
                    "message": "No Calendly access token configured"
                }
                
            token_preview = token[:5] + "..." if len(token) > 5 else "<empty>"
            logger.info(f"[CALENDLY DEBUG] Using Calendly access token starting with: {token_preview}")
            
            # Create Calendly service
            calendly_service = CalendlyService(CalendlyConfig(
                enabled=True,
                access_token=token,
                user_uri=calendly_config.get('user_uri'),
                default_event_type=calendly_config.get('default_event_type', ''),
                booking_window_days=calendly_config.get('booking_window_days', 14),
                min_notice_hours=calendly_config.get('min_notice_hours', 1),
            ))
            
            # Check if we need to initialize to get user_uri
            if not calendly_config.get('user_uri'):
                logger.info("[CALENDLY DEBUG] No user_uri found, attempting to initialize Calendly service")
                try:
                    user_uri = await calendly_service.initialize()
                    logger.info(f"[CALENDLY DEBUG] Initialized Calendly service, user_uri: {user_uri}")
                except Exception as init_error:
                    logger.error(f"[CALENDLY DEBUG] Failed to initialize Calendly service: {str(init_error)}")
                    logger.error(f"[CALENDLY DEBUG] Initialization error details: {traceback.format_exc()}")
                    return {
                        "success": False,
                        "error": "Initialization Error",
                        "message": f"Failed to initialize Calendly: {str(init_error)}"
                    }
            
            # Call the verification method directly
            logger.info("[CALENDLY DEBUG] Calling Calendly verify_appointment method")
            try:
                verification_result = await calendly_service.verify_appointment(search_date)
                
                logger.info(f"[CALENDLY DEBUG] Successfully verified appointment: {verification_result}")
                
                # Log important details for debugging
                if verification_result.get("exists"):
                    logger.info("[CALENDLY DEBUG] Found an existing appointment")
                else:
                    logger.info(f"[CALENDLY DEBUG] No exact appointment found. Available slots: {len(verification_result.get('available_slots', []))}")
                    if verification_result.get('available_slots'):
                        sample_slots = verification_result.get('available_slots')[:2]
                        logger.info(f"[CALENDLY DEBUG] Sample available slots: {sample_slots}")
                
                return {
                    "success": True,
                    "verification": verification_result
                }
            except Exception as verify_error:
                logger.error(f"[CALENDLY DEBUG] Error verifying appointment: {str(verify_error)}")
                logger.error(f"[CALENDLY DEBUG] Verification error details: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": "Verification Error",
                    "message": f"Failed to verify appointment: {str(verify_error)}"
                }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"[CALENDLY DEBUG] Exception in verify_appointment: {str(e)}")
        logger.error(f"[CALENDLY DEBUG] Stack trace: {traceback.format_exc()}")
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
