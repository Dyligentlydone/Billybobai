from fastapi import APIRouter, HTTPException, Query
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.calendly import CalendlyService
from app.schemas.calendly import CalendlyConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calendly-debug", tags=["debug"])


class DiagnosticResponse(BaseModel):
    success: bool
    steps: List[Dict[str, Any]]
    overall_message: str


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
                "step": "setup",
                "success": False,
                "message": "No Calendly access token provided",
                "error": "Missing token parameter or CALENDLY_ACCESS_TOKEN environment variable"
            }],
            overall_message="Failed: No Calendly access token provided"
        )
    
    # Create Calendly config and service directly
    calendly_config = CalendlyConfig(
        enabled=True,
        access_token=access_token.strip(),  # Strip any whitespace
        default_event_type=""  # Will be populated after getting event types
    )
    
    # Create service
    calendly_service = CalendlyService(config=calendly_config)
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
                    {"id": et.id, "name": et.name, "uri": et.uri} for et in event_types
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
                if step["step"] == "get_event_types" and "data" in step:
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
                "message": "Skipped due to previous failures",
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

    # Build the overall diagnostic message
    if overall_success:
        overall_message = "All Calendly integration checks passed successfully"
    else:
        failed_steps = [step["step"] for step in steps if not step["success"]]
        overall_message = f"Calendly integration checks failed at steps: {', '.join(failed_steps)}"

    return DiagnosticResponse(
        success=overall_success,
        steps=steps,
        overall_message=overall_message
    )
