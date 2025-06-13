from fastapi import APIRouter, HTTPException, Query
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.calendly import CalendlyService
from app.schemas.calendly import CalendlyConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calendly-debug", tags=["debug"])

# Configure detailed logging for development
logging.basicConfig(level=logging.INFO)


class DiagnosticResponse(BaseModel):
    success: bool
    steps: List[Dict[str, Any]]
    overall_message: str


class AvailabilityResponse(BaseModel):
    success: bool
    message: str
    days_checked: int
    available_days: List[Dict[str, Any]]
    available_days_names: List[str]
    using_fallback: bool
    error: Optional[str] = None


@router.get("/diagnostics", response_model=DiagnosticResponse)
async def run_calendly_diagnostics(
    token: Optional[str] = Query(None, description="Calendly API token (optional if set in environment)"),
):
    """
    Run a complete diagnostic check on Calendly integration
    """
    steps = []
    overall_success = True
    
    # Get token from query parameter or environment
    access_token = token or os.environ.get("CALENDLY_ACCESS_TOKEN", "")
    if not access_token:
        return DiagnosticResponse(
            success=False,
            steps=[{
                "name": "Token Check",
                "success": False,
                "message": "No Calendly access token provided. Please provide a token or set CALENDLY_ACCESS_TOKEN environment variable."
            }],
            overall_message="Diagnostics failed: No access token provided"
        )
    
    # Initialize Calendly service
    config = CalendlyConfig(access_token=access_token)
    calendly = CalendlyService(config)
    
    try:
        # Step 1: Initialize and get user info
        steps.append({"name": "Initialization", "status": "running", "message": "Initializing Calendly service..."})        
        await calendly.initialize()
        
        if not calendly.config.user_uri:
            steps[-1].update({"success": False, "status": "failed", "message": "Failed to initialize: Could not retrieve user URI"})
            overall_success = False
        else:
            steps[-1].update({
                "success": True, 
                "status": "completed", 
                "message": f"Successfully initialized with user URI: {calendly.config.user_uri}",
                "user_uri": calendly.config.user_uri
            })
        
        # Step 2: Get event types
        steps.append({"name": "Event Types", "status": "running", "message": "Fetching event types..."})        
        event_types = await calendly.get_event_types()
        
        if not event_types:
            steps[-1].update({"success": False, "status": "failed", "message": "No event types found"})
            overall_success = False
        else:
            event_types_data = [{
                "id": et.id,
                "name": et.name,
                "duration": et.duration,
                "description": et.description[:50] + "..." if et.description and len(et.description) > 50 else et.description
            } for et in event_types]
            
            steps[-1].update({
                "success": True, 
                "status": "completed", 
                "message": f"Successfully retrieved {len(event_types)} event types",
                "event_types": event_types_data
            })
        
        # Step 3: Get available slots for first event type
        if event_types:
            steps.append({"name": "Available Slots", "status": "running", "message": "Fetching available slots..."})
            
            # Use the first event type for testing
            test_event_type = event_types[0].id
            start_time = datetime.now()
            days = 7
            
            try:
                slots = await calendly.get_available_slots(test_event_type, start_time, days)
                
                if not slots:
                    steps[-1].update({
                        "success": True,  # Still consider this a success, just no slots available
                        "status": "completed", 
                        "message": f"No available slots found for event type '{event_types[0].name}' in the next {days} days"
                    })
                else:
                    slots_data = [{
                        "date": slot.start_time.strftime("%Y-%m-%d"),
                        "start": slot.start_time.strftime("%H:%M"),
                        "end": slot.end_time.strftime("%H:%M"),
                    } for slot in slots[:5]]  # Limit to first 5 slots for brevity
                    
                    steps[-1].update({
                        "success": True, 
                        "status": "completed", 
                        "message": f"Found {len(slots)} available slots for event type '{event_types[0].name}'",
                        "slots_sample": slots_data,
                        "total_slots": len(slots)
                    })
            except Exception as e:
                steps[-1].update({
                    "success": False, 
                    "status": "failed", 
                    "message": f"Error fetching available slots: {str(e)}"
                })
                overall_success = False
    
    except Exception as e:
        steps.append({
            "name": "Unexpected Error", 
            "success": False, 
            "status": "failed", 
            "message": f"An unexpected error occurred: {str(e)}"
        })
        overall_success = False
    
    # Generate overall message
    if overall_success:
        overall_message = "All Calendly API tests passed successfully!"
    else:
        overall_message = "Some Calendly API tests failed. See steps for details."
    
    return DiagnosticResponse(
        success=overall_success,
        steps=steps,
        overall_message=overall_message
    )
    logger.info("[CALENDLY DEBUG] Created service for diagnostics")
    
    # Step 1: Check if we can initialize and get user URI
    try:
        user_uri = await calendly_service.initialize()
        steps.append({
            "step": "initialize",
            "success": True,
            "message": f"Successfully initialized with user URI: {user_uri}",
            "data": {"user_uri": user_uri}
        })
    except Exception as e:
        overall_success = False
        steps.append({
            "step": "initialize",
            "success": False,
            "message": f"Failed to initialize: {str(e)}",
            "error": str(e)
        })
        return DiagnosticResponse(
            success=False,
            steps=steps,
            overall_message="Failed to initialize Calendly service. Check access token and permissions."
        )

    # Step 2: Get event types
    try:
        event_types = await calendly_service.get_event_types()
        steps.append({
            "step": "get_event_types",
            "success": True,
            "message": f"Found {len(event_types)} event types",
            "data": {
                "count": len(event_types),
                "types": [
                    {"id": et.id, "name": et.name, "duration": et.duration} for et in event_types
                ]
            }
        })
    except Exception as e:
        overall_success = False
        steps.append({
            "step": "get_event_types",
            "success": False,
            "message": f"Failed to get event types: {str(e)}",
            "error": str(e)
        })

    # Step 3: Try to get scheduled events for next 7 days
    now = datetime.now()
    in_7_days = now + timedelta(days=7)
    
    try:
        events = await calendly_service.get_scheduled_events(now, in_7_days)
        steps.append({
            "step": "get_scheduled_events",
            "success": True,
            "message": f"Found {len(events)} scheduled events for the next 7 days",
            "data": {
                "count": len(events),
                "date_range": {
                    "start": now.isoformat(),
                    "end": in_7_days.isoformat()
                }
            }
        })
    except Exception as e:
        steps.append({
            "step": "get_scheduled_events",
            "success": False,
            "message": f"Failed to get scheduled events: {str(e)}",
            "error": str(e)
        })
        # Not marking as overall failure since our fix should handle this case

    # Step 4: Try to get available slots for the first event type
    try:
        # Only proceed if we got event types successfully
        if any(step["step"] == "get_event_types" and step["success"] for step in steps):
            event_type = None
            for step in steps:
                if step["step"] == "get_event_types" and step["success"] and "data" in step:
                    if step["data"]["count"] > 0:
                        event_type = step["data"]["types"][0]
                        break
            
            if event_type:
                slots = await calendly_service.get_available_slots(
                    event_type["id"], start_time=now, days=7
                )
                steps.append({
                    "step": "get_available_slots",
                    "success": True,
                    "message": f"Found {len(slots)} available slots for event type: {event_type['name']}",
                    "data": {
                        "count": len(slots),
                        "event_type_id": event_type["id"],
                        "slots": [
                            {
                                "start": slot.start_time.isoformat(),
                                "end": slot.end_time.isoformat()
                            } 
                            for slot in slots[:5]  # Just show first 5 to keep response size reasonable
                        ],
                        "has_more": len(slots) > 5
                    }
                })
            else:
                steps.append({
                    "step": "get_available_slots",
                    "success": False,
                    "message": "No event types available to check slots",
                    "error": "No event types found"
                })
                overall_success = False
        else:
            steps.append({
                "step": "get_available_slots",
                "success": False,
                "message": "Could not check availability - event types not available",
                "error": "Event types retrieval failed"
            })
    except Exception as e:
        overall_success = False
        steps.append({
            "step": "get_available_slots",
            "success": False,
            "message": f"Failed to get available slots: {str(e)}",
            "error": str(e)
        })

    # Step 5: Test the verify_appointment flow with current datetime
    try:
        verification = await calendly_service.verify_appointment(datetime.now())
        steps.append({
            "step": "verify_appointment",
            "success": True,
            "message": "Successfully ran appointment verification",
            "data": {
                "exists": verification.get("exists", False),
                "available_slots_count": len(verification.get("available_slots", [])),
            }
        })
    except Exception as e:
        overall_success = False
        steps.append({
            "step": "verify_appointment",
            "success": False,
            "message": f"Failed to verify appointment: {str(e)}",
            "error": str(e)
        })

    # Recalculate overall_success based on actual step results
    # Only count critical steps as failures (initialize and get_event_types)
    critical_failures = [step for step in steps if not step["success"] and step["step"] in ["initialize", "get_event_types"]]
    overall_success = len(critical_failures) == 0
    
    # Build the overall diagnostic message
    if overall_success:
        overall_message = "All critical Calendly integration checks passed successfully"
    else:
        failed_steps = [step["step"] for step in critical_failures]
        overall_message = f"Calendly integration checks failed at critical steps: {', '.join(failed_steps)}"

    return DiagnosticResponse(
        success=overall_success,
        steps=steps,
        overall_message=overall_message
    )


@router.get("/test-availability", response_model=AvailabilityResponse)
async def test_availability(
    token: Optional[str] = Query(None, description="Calendly API token (optional if set in environment)"),
    days: int = Query(7, description="Number of days to check for availability"),
    force_fallback: bool = Query(False, description="Force using fallback availability")
):
    """
    Test Calendly availability directly to debug why real data isn't being used
    """
    logger.info(f"[CALENDLY TEST] Starting availability test for {days} days")
    
    try:
        # Get token from query parameter or environment
        access_token = token or os.environ.get("CALENDLY_ACCESS_TOKEN", "")
        if not access_token:
            return AvailabilityResponse(
                success=False,
                message="No Calendly access token provided",
                days_checked=days,
                available_days=[],
                available_days_names=[],
                using_fallback=True,
                error="Missing token parameter or CALENDLY_ACCESS_TOKEN environment variable"
            )
        
        # Create Calendly config and service directly
        calendly_config = CalendlyConfig(
            enabled=True,
            access_token=access_token.strip(),  # Strip any whitespace
            default_event_type=""  # Will be populated after getting event types
        )
        
        # Create service
        calendly_service = CalendlyService(config=calendly_config)
        logger.info(f"[CALENDLY TEST] Created service with token length: {len(access_token)}")
        
        # Initialize service first (required for proper API calls)
        user_uri = await calendly_service.initialize()
        logger.info(f"[CALENDLY TEST] Successfully initialized with user URI: {user_uri}")
        
        # If forcing fallback, modify the service temporarily
        original_get_available_slots = None
        if force_fallback:
            logger.info(f"[CALENDLY TEST] Forcing fallback availability for testing")
            # Save the original method and replace it with one that always raises an exception
            original_get_available_slots = calendly_service.get_available_slots
            
            async def force_fallback_slots(*args, **kwargs):
                raise Exception("Forced fallback for testing")
            
            calendly_service.get_available_slots = force_fallback_slots
        
        # Get available days
        start_time = datetime.now()
        available_days_result = await calendly_service.get_available_days(days=days, start_date=start_time)
        
        # Restore the original method if needed
        if force_fallback and original_get_available_slots:
            calendly_service.get_available_slots = original_get_available_slots
        
        # Check if fallback was used
        using_fallback = available_days_result.get("using_fallback", True)
        available_days = available_days_result.get("available_days", [])
        day_names = [day["day_name"] for day in available_days]
        
        # Get diagnostic information on why fallback might have happened
        diagnostics = {
            "user_uri": calendly_service.config.user_uri,
            "token_length": len(access_token) if access_token else 0,
            "event_types": []
        }
        
        # Try to get event types for diagnostics
        try:
            event_types = await calendly_service.get_event_types()
            diagnostics["event_types"] = [
                {"id": et.id, "name": et.name, "slug": et.slug} 
                for et in event_types
            ]
            diagnostics["default_event_type"] = calendly_service.config.default_event_type
        except Exception as e:
            diagnostics["event_types_error"] = str(e)
        
        # Create message based on results
        if using_fallback:
            message = f"Using FALLBACK data. Available days: {', '.join(day_names)}"
        else:
            message = f"Using REAL Calendly data. Available days: {', '.join(day_names)}"
        
        return AvailabilityResponse(
            success=True,
            message=message,
            days_checked=days,
            available_days=available_days,
            available_days_names=day_names,
            using_fallback=using_fallback,
            error=None
        )
    except Exception as e:
        logger.error(f"[CALENDLY TEST] Error testing availability: {str(e)}")
        return AvailabilityResponse(
            success=False,
            message=f"Error: {str(e)}",
            days_checked=days,
            available_days=[],
            available_days_names=[],
            using_fallback=True,
            error=str(e)
        )
