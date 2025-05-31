from datetime import datetime
import logging
from typing import Dict, Any, Optional
import traceback

# Import directly from services to avoid circular imports
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.workflow import Workflow

logger = logging.getLogger(__name__)

async def verify_appointment_with_service(business_id: str, search_date: datetime) -> Dict[str, Any]:
    """
    Directly call the Calendly service to verify if an appointment exists or get available days
    
    Args:
        business_id: The business/workflow ID
        search_date: The date/time to verify
        
    Returns:
        Dict containing verification results or availability information
    """
    try:
        # Import here to avoid circular imports
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from ..services.calendly import CalendlyService
        else:
            # Import dynamically to avoid circular imports
            import importlib
            calendly_module = importlib.import_module("..services.calendly", package=__package__)
            CalendlyService = getattr(calendly_module, "CalendlyService")
        
        from ..schemas.calendly import CalendlyConfig
        
        logger.info(f"[CALENDLY DEBUG] Verifying appointment for business {business_id} at {search_date}")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get workflow and check if Calendly is configured
            workflow = db.query(Workflow).filter(Workflow.id == business_id).first()
            
            if not workflow:
                logger.error(f"[CALENDLY DEBUG] Workflow not found for ID {business_id}")
                return {
                    "success": False,
                    "error": "Not Found",
                    "message": f"Workflow {business_id} not found"
                }
                
            # Log the entire workflow for debugging
            logger.info(f"[CALENDLY DEBUG] Full workflow object: id={workflow.id}, name={workflow.name}")
            logger.info(f"[CALENDLY DEBUG] Config column type: {type(workflow.config).__name__}")
            logger.info(f"[CALENDLY DEBUG] Actions column type: {type(workflow.actions).__name__}")
            logger.info(f"[CALENDLY DEBUG] Config keys: {list(workflow.config.keys()) if workflow.config else 'None'}")
            logger.info(f"[CALENDLY DEBUG] Actions keys: {list(workflow.actions.keys()) if workflow.actions else 'None'}")
            
            # Check if 'calendly' exists in either column
            if workflow.config and 'calendly' in workflow.config:
                logger.info(f"[CALENDLY DEBUG] Found 'calendly' in config column with keys: {list(workflow.config['calendly'].keys()) if isinstance(workflow.config['calendly'], dict) else 'Not a dict'}")
            
            if workflow.actions and 'calendly' in workflow.actions:
                logger.info(f"[CALENDLY DEBUG] Found 'calendly' in actions column with keys: {list(workflow.actions['calendly'].keys()) if isinstance(workflow.actions['calendly'], dict) else 'Not a dict'}")

                
            # Let's be thorough in finding the Calendly config, checking all possible locations
            calendly_config = {}
            possible_locations = [
                # Check direct in actions
                ('actions.calendly', workflow.actions.get('calendly') if workflow.actions else None),
                # Check direct in config
                ('config.calendly', workflow.config.get('calendly') if workflow.config else None),
                # Check in integrations
                ('actions.integrations.calendly', 
                 workflow.actions.get('integrations', {}).get('calendly') if workflow.actions else None),
                # Check in systemIntegration (based on user's screenshot)
                ('actions.systemIntegration.calendly',
                 workflow.actions.get('systemIntegration', {}).get('calendly') if workflow.actions else None),
                ('config.systemIntegration.calendly',
                 workflow.config.get('systemIntegration', {}).get('calendly') if workflow.config else None),
                # Check if config itself is the calendly config (in case of unusual structure)
                ('config_direct', workflow.config if workflow.config and 'access_token' in workflow.config else None),
                # Check if actions itself is the calendly config (in case of unusual structure)
                ('actions_direct', workflow.actions if workflow.actions and 'access_token' in workflow.actions else None),
            ]
            
            # Dump all top-level keys for diagnosis
            if workflow.config:
                logger.info(f"[CALENDLY DEBUG] Config object type: {type(workflow.config).__name__}")
                logger.info(f"[CALENDLY DEBUG] Complete config structure: {workflow.config}")
            if workflow.actions:
                logger.info(f"[CALENDLY DEBUG] Actions object type: {type(workflow.actions).__name__}")
                for key, value in workflow.actions.items():
                    logger.info(f"[CALENDLY DEBUG] Action key '{key}' has type: {type(value).__name__}")
                    if key == 'systemIntegration' and isinstance(value, dict):
                        logger.info(f"[CALENDLY DEBUG] SystemIntegration keys: {list(value.keys())}")
                        if 'calendly' in value:
                            logger.info(f"[CALENDLY DEBUG] Found calendly in systemIntegration with access_token: {'access_token' in value['calendly']}")

            
            # Log all locations
            for location_name, config in possible_locations:
                logger.info(f"[CALENDLY DEBUG] Checking {location_name}: {'Found data' if config else 'Empty'}")
                if config and isinstance(config, dict) and 'access_token' in config:
                    logger.info(f"[CALENDLY DEBUG] Found access_token in {location_name}!")
                    calendly_config = config
                    break
                    
            # Special check for systemIntegration.calendly path (based on user's screenshot)
            if not calendly_config.get('access_token'):
                if workflow.actions and 'systemIntegration' in workflow.actions:
                    system_integration = workflow.actions.get('systemIntegration', {})
                    if isinstance(system_integration, dict) and 'calendly' in system_integration:
                        calendly_in_sys = system_integration.get('calendly', {})
                        if isinstance(calendly_in_sys, dict) and 'access_token' in calendly_in_sys:
                            logger.info(f"[CALENDLY DEBUG] Found access_token in actions.systemIntegration.calendly!")
                            calendly_config = calendly_in_sys
                            
                if workflow.config and 'systemIntegration' in workflow.config:
                    system_integration = workflow.config.get('systemIntegration', {})
                    if isinstance(system_integration, dict) and 'calendly' in system_integration:
                        calendly_in_sys = system_integration.get('calendly', {})
                        if isinstance(calendly_in_sys, dict) and 'access_token' in calendly_in_sys:
                            logger.info(f"[CALENDLY DEBUG] Found access_token in config.systemIntegration.calendly!")
                            calendly_config = calendly_in_sys
            
            logger.info(f"[CALENDLY DEBUG] Final Calendly config: {calendly_config}")

            
            # Check if Calendly is configured and access token exists
            if not calendly_config or not calendly_config.get('access_token'):
                logger.error(f"[CALENDLY DEBUG] No valid Calendly configuration found with access token")
                return {
                    "success": False, 
                    "error": "Configuration Error",
                    "message": "Calendly access token not found in configuration"
                }
                
            # Log that we've found a valid configuration
            token_preview = calendly_config.get('access_token', '')[:5] + '...' if calendly_config.get('access_token') else 'None'
            logger.info(f"[CALENDLY DEBUG] Found valid Calendly configuration with access token: {token_preview}")
            
            # Create config object for Calendly service
            config = CalendlyConfig(
                access_token=calendly_config.get('access_token'),
                user_uri=calendly_config.get('user_uri'),
                enabled=True
            )
            
            # Initialize the Calendly service
            calendly_service = CalendlyService(config)
            logger.info(f"[CALENDLY DEBUG] Created Calendly service with config: {config}")
            
            # Check if we need to initialize to get user_uri
            if not calendly_config.get('user_uri'):
                logger.info("[CALENDLY DEBUG] No user_uri found, attempting to initialize Calendly service")
                try:
                    user_uri = await calendly_service.initialize()
                    logger.info(f"[CALENDLY DEBUG] Initialized Calendly service, user_uri: {user_uri}")
                except Exception as init_error:
                    error_tb = traceback.format_exc()
                    logger.error(f"[CALENDLY DEBUG] Failed to initialize Calendly service: {str(init_error)}")
                    logger.error(f"[CALENDLY DEBUG] Initialization error details: {error_tb}")
                    return {
                        "success": False,
                        "error": "Initialization Error",
                        "message": f"Failed to initialize Calendly: {str(init_error)}"
                    }
            
            # Determine if this is a general availability query ("what days are available next week?")
            # or a specific appointment verification query
            
            # Check if the date is for "next week" - this is a heuristic for detecting availability queries
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            next_week_start = today + timedelta(days=(7 - today.weekday()))
            next_week_end = next_week_start + timedelta(days=6)
            
            # If the date is in the next week range or missing specific time, treat as an availability query
            is_availability_query = False
            if search_date.hour == 0 and search_date.minute == 0:  # Only date was provided, not time
                is_availability_query = True
                logger.info(f"[CALENDLY DEBUG] Detected availability query - no specific time")
            elif next_week_start <= search_date.replace(hour=0, minute=0, second=0, microsecond=0) <= next_week_end:
                # Query is for next week
                is_availability_query = True
                logger.info(f"[CALENDLY DEBUG] Detected availability query - date is next week")
                
            if is_availability_query:
                # Get available days for next week
                start_date = next_week_start
                logger.info(f"[CALENDLY DEBUG] Getting available days for next week starting {start_date}")
                
                # Call the new get_available_days method
                availability_result = await calendly_service.get_available_days(
                    days=7,  # One week
                    start_date=start_date
                )
                logger.info(f"[CALENDLY DEBUG] Available days result: {availability_result}")
                
                # Return success result with availability information
                return {
                    "success": True,
                    "is_availability_query": True,
                    "verification": {
                        "exists": False,  # No specific appointment
                        "details": None,
                        "closest_time": None,
                        "available_slots": availability_result.get("available_days", []),
                        "search_date": search_date.isoformat(),
                        "message": availability_result.get("message", "")
                    },
                    "availability": availability_result
                }
            else:
                # Regular appointment verification
                verification_result = await calendly_service.verify_appointment(search_date)
                logger.info(f"[CALENDLY DEBUG] Verification result: {verification_result}")
                
                # Return success result
                return {
                    "success": True,
                    "is_availability_query": False,
                    "verification": verification_result
                }
        except Exception as verify_error:
            error_tb = traceback.format_exc()
            logger.error(f"[CALENDLY DEBUG] Error verifying appointment: {str(verify_error)}")
            logger.error(f"[CALENDLY DEBUG] Verification error details: {error_tb}")
            return {
                "success": False,
                "error": "Verification Error",
                "message": f"Failed to verify appointment: {str(verify_error)}"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        error_tb = traceback.format_exc()
        logger.error(f"[CALENDLY DEBUG] Exception in verify_appointment: {str(e)}")
        logger.error(f"[CALENDLY DEBUG] Stack trace: {error_tb}")
        return {
            "success": False,
            "error": "Internal Error",
            "message": str(e)
        }

async def create_appointment_with_service(business_id: str, date_time: datetime, name: str, email: str, phone: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an appointment in Calendly using the service
    
    Args:
        business_id: The business/workflow ID
        date_time: The date and time for the appointment
        name: Customer's name
        email: Customer's email address
        phone: Customer's phone number (optional)
        
    Returns:
        Dict containing booking results
    """
    try:
        # Import here to avoid circular imports
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from ..services.calendly import CalendlyService
        else:
            # Import dynamically to avoid circular imports
            import importlib
            calendly_module = importlib.import_module("..services.calendly", package=__package__)
            CalendlyService = getattr(calendly_module, "CalendlyService")
        
        from ..schemas.calendly import CalendlyConfig
        import traceback
        
        logger.info(f"[CALENDLY DEBUG] Creating appointment for business {business_id} at {date_time}")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get workflow and check if Calendly is configured
            workflow = db.query(Workflow).filter(Workflow.id == business_id).first()
            
            if not workflow:
                logger.error(f"[CALENDLY DEBUG] Workflow not found for ID {business_id}")
                return {
                    "success": False,
                    "error": "Not Found",
                    "message": f"Workflow {business_id} not found"
                }
            
            # Let's be thorough in finding the Calendly config, checking all possible locations
            calendly_config = {}
            possible_locations = [
                # Check direct in actions
                ('actions.calendly', workflow.actions.get('calendly') if workflow.actions else None),
                # Check direct in config
                ('config.calendly', workflow.config.get('calendly') if workflow.config else None),
                # Check in integrations
                ('actions.integrations.calendly', 
                 workflow.actions.get('integrations', {}).get('calendly') if workflow.actions else None),
                # Check in systemIntegration (based on user's screenshot)
                ('actions.systemIntegration.calendly',
                 workflow.actions.get('systemIntegration', {}).get('calendly') if workflow.actions else None),
                ('config.systemIntegration.calendly',
                 workflow.config.get('systemIntegration', {}).get('calendly') if workflow.config else None),
                # Check if config itself is the calendly config (in case of unusual structure)
                ('config_direct', workflow.config if workflow.config and 'access_token' in workflow.config else None),
                # Check if actions itself is the calendly config (in case of unusual structure)
                ('actions_direct', workflow.actions if workflow.actions and 'access_token' in workflow.actions else None),
            ]
            
            # Log all locations
            for location_name, config in possible_locations:
                logger.info(f"[CALENDLY DEBUG] Checking {location_name}: {'Found data' if config else 'Empty'}")
                if config and isinstance(config, dict) and 'access_token' in config:
                    logger.info(f"[CALENDLY DEBUG] Found access_token in {location_name}!")
                    calendly_config = config
                    break
                    
            # Special check for systemIntegration.calendly path (based on user's screenshot)
            if not calendly_config.get('access_token'):
                if workflow.actions and 'systemIntegration' in workflow.actions:
                    system_integration = workflow.actions.get('systemIntegration', {})
                    if isinstance(system_integration, dict) and 'calendly' in system_integration:
                        calendly_in_sys = system_integration.get('calendly', {})
                        if isinstance(calendly_in_sys, dict) and 'access_token' in calendly_in_sys:
                            logger.info(f"[CALENDLY DEBUG] Found access_token in actions.systemIntegration.calendly!")
                            calendly_config = calendly_in_sys
                            
                if workflow.config and 'systemIntegration' in workflow.config:
                    system_integration = workflow.config.get('systemIntegration', {})
                    if isinstance(system_integration, dict) and 'calendly' in system_integration:
                        calendly_in_sys = system_integration.get('calendly', {})
                        if isinstance(calendly_in_sys, dict) and 'access_token' in calendly_in_sys:
                            logger.info(f"[CALENDLY DEBUG] Found access_token in config.systemIntegration.calendly!")
                            calendly_config = calendly_in_sys
            
            logger.info(f"[CALENDLY DEBUG] Final Calendly config: {calendly_config}")
            
            # Check if Calendly is configured
            if not calendly_config or not calendly_config.get('access_token'):
                logger.error(f"[CALENDLY DEBUG] No valid Calendly configuration found with access token")
                return {
                    "success": False,
                    "error": "Configuration Error",
                    "message": "Calendly access token not found in configuration"
                }
            
            # Create the Calendly service
            if isinstance(calendly_config, dict):
                # Convert dict to CalendlyConfig object
                # Include all the fields that are in the dict
                config_obj = CalendlyConfig(
                    enabled=True,
                    access_token=calendly_config.get('access_token'),
                    user_uri=calendly_config.get('user_uri'),
                    webhook_uri=calendly_config.get('webhook_uri'),
                    default_event_type=calendly_config.get('default_event_type', ''),
                )
                logger.info(f"[CALENDLY DEBUG] Created Calendly service with config: {config_obj}")
                calendly_service = CalendlyService(config_obj)
                
                # Initialize the service if needed (will auto-fetch user URI if not provided)
                if not config_obj.user_uri:
                    await calendly_service.initialize()
                
                # Get the default event type from config
                default_event_type = calendly_config.get('default_event_type', '')
                
                # Check if we have a valid event type
                if not default_event_type:
                    logger.error(f"[CALENDLY DEBUG] No default event type configured for this account")
                    return {
                        "success": False,
                        "error": "Configuration Error",
                        "message": "No default event type is configured. Please select an event type in the SMS configuration."
                    }
                
                # At this point we have a default_event_type which could be:
                # 1. A slug like "consultation-demo"
                # 2. A full URI like "https://api.calendly.com/event_types/abc123/consultation-demo"
                # 3. An ID or partial path
                # The service will handle proper formatting to a full URI
                
                # Log what we're using
                logger.info(f"[CALENDLY DEBUG] Using event type: {default_event_type}")
                
                # Create the appointment
                booking_result = await calendly_service.create_appointment(
                    date_time=date_time, 
                    name=name,
                    email=email,
                    phone=phone,
                    event_type_id=default_event_type
                )
                
                logger.info(f"[CALENDLY DEBUG] Booking result: {booking_result}")
                return booking_result
            else:
                logger.error(f"[CALENDLY DEBUG] Calendly configuration is not a dictionary: {type(calendly_config)}")
                return {
                    "success": False,
                    "error": "Configuration Error",
                    "message": "Invalid Calendly configuration format"
                }
            
        except Exception as verify_error:
            error_tb = traceback.format_exc()
            logger.error(f"[CALENDLY DEBUG] Error creating appointment: {str(verify_error)}")
            logger.error(f"[CALENDLY DEBUG] Booking error details: {error_tb}")
            return {
                "success": False,
                "error": "Booking Error",
                "message": f"Failed to create appointment: {str(verify_error)}"
            }
        
        finally:
            db.close()
            
    except Exception as e:
        error_tb = traceback.format_exc()
        logger.error(f"[CALENDLY DEBUG] Exception in create_appointment: {str(e)}")
        logger.error(f"[CALENDLY DEBUG] Stack trace: {error_tb}")
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
    
    # Check if this is an availability query (what days are available next week?)
    if verification_result.get("is_availability_query", False):
        # If there's a custom message, use that
        if "availability" in verification_result and verification_result["availability"].get("message"):
            return verification_result["availability"]["message"]
            
        # Otherwise, format the available days
        verification = verification_result.get("verification", {})
        available_slots = verification.get("available_slots", [])
        
        if not available_slots or len(available_slots) == 0:
            return "I don't see any available appointment slots for next week."
            
        # Group slots by day
        days_with_slots = {}
        for slot in available_slots:
            day_name = slot.get("day_name", "")
            if day_name and day_name not in days_with_slots:
                days_with_slots[day_name] = True
                
        if days_with_slots:
            day_names = list(days_with_slots.keys())
            if len(day_names) == 1:
                return f"We have availability next week on {day_names[0]}."
            elif len(day_names) == 2:
                return f"We have availability next week on {day_names[0]} and {day_names[1]}."
            else:
                day_list = ", ".join(day_names[:-1]) + f", and {day_names[-1]}"
                return f"We have availability next week on {day_list}."
        else:
            return "I don't see any available appointment slots for next week."
    
    # Regular appointment verification
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
        
        # If there's a custom message, use that
        if verification.get("message"):
            return verification.get("message")
            
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
