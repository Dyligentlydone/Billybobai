from fastapi import APIRouter, Query
from datetime import datetime
import httpx
import logging
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calendly-raw", tags=["debug"])


class RawAPIResponse(BaseModel):
    success: bool
    status_code: int
    url: str
    response_body: Dict[str, Any]
    headers_sent: Dict[str, str]


@router.get("/direct", response_model=RawAPIResponse)
async def test_direct_calendly_api(
    token: str = Query(..., description="Calendly API token"),
    url: str = Query("https://api.calendly.com/users/me", description="API URL to test"),
):
    """
    Make a direct raw request to Calendly API for debugging.
    This bypasses all our service layers and makes a direct HTTP request.
    """
    logger.info(f"Making direct request to Calendly API: {url}")
    
    # Clean the token
    clean_token = token.strip()
    
    # Create headers
    headers = {
        "Authorization": f"Bearer {clean_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make direct request to Calendly API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            # Log status code
            logger.info(f"Direct request status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_body = response.json()
            except Exception:
                response_body = {"text": response.text}
                
            # Return the raw response details
            return RawAPIResponse(
                success=(response.status_code == 200),
                status_code=response.status_code,
                url=url,
                response_body=response_body,
                headers_sent={k: v for k, v in headers.items() if k != "Authorization"}  # Don't include actual token
            )
    except Exception as e:
        logger.error(f"Error making direct request: {str(e)}")
        return RawAPIResponse(
            success=False,
            status_code=500,
            url=url,
            response_body={"error": str(e)},
            headers_sent={k: v for k, v in headers.items() if k != "Authorization"}
        )


@router.get("/user-info")
async def get_user_info(
    token: str = Query(..., description="Calendly API token")
):
    """
    Get Calendly user info using direct API calls
    """
    return await test_direct_calendly_api(token=token, url="https://api.calendly.com/users/me")


@router.get("/event-types")
async def get_event_types(
    token: str = Query(..., description="Calendly API token"),
    user_uuid: Optional[str] = Query(None, description="User UUID (extracted from user URI)")
):
    """
    Get event types for a user using direct API calls
    """
    if not user_uuid:
        # Try to get user info first
        user_info_response = await get_user_info(token=token)
        if user_info_response.success and "resource" in user_info_response.response_body:
            user_uri = user_info_response.response_body["resource"].get("uri")
            if user_uri:
                # Extract UUID from URI
                user_uuid = user_uri.split("/")[-1]
    
    if not user_uuid:
        return RawAPIResponse(
            success=False,
            status_code=400,
            url="N/A",
            response_body={"error": "Could not determine user UUID"},
            headers_sent={}
        )
        
    # Try to get event types using the user UUID
    url = f"https://api.calendly.com/users/{user_uuid}/event_types"
    return await test_direct_calendly_api(token=token, url=url)


@router.get("/scheduled-events")
async def get_scheduled_events(
    token: str = Query(..., description="Calendly API token"),
    user_uuid: Optional[str] = Query(None, description="User UUID (extracted from user URI)")
):
    """
    Get scheduled events for a user using direct API calls
    """
    if not user_uuid:
        # Try to get user info first
        user_info_response = await get_user_info(token=token)
        if user_info_response.success and "resource" in user_info_response.response_body:
            user_uri = user_info_response.response_body["resource"].get("uri")
            if user_uri:
                # Extract UUID from URI
                user_uuid = user_uri.split("/")[-1]
    
    if not user_uuid:
        return RawAPIResponse(
            success=False,
            status_code=400,
            url="N/A",
            response_body={"error": "Could not determine user UUID"},
            headers_sent={}
        )
        
    # Try to get scheduled events using the user UUID
    url = f"https://api.calendly.com/users/{user_uuid}/scheduled_events"
    return await test_direct_calendly_api(token=token, url=url)


@router.get("/try-all")
async def try_all_endpoints(
    token: str = Query(..., description="Calendly API token")
):
    """
    Try multiple Calendly API endpoints to determine which ones work
    """
    try:
        # Step 1: Get user info
        user_response = await get_user_info(token=token)
        
        # Extract user UUID and other useful information if successful
        user_uuid = None
        username = None
        organization_uri = None
        
        if user_response and hasattr(user_response, 'success') and user_response.success:
            if hasattr(user_response, 'response_body') and isinstance(user_response.response_body, dict) and "resource" in user_response.response_body:
                user_data = user_response.response_body["resource"]
                
                # Get user URI
                user_uri = user_data.get("uri", "")
                if user_uri:
                    try:
                        user_uuid = user_uri.split("/")[-1]
                    except Exception as e:
                        logger.error(f"Error extracting user UUID: {e}")
                
                # Extract username from email
                email = user_data.get("email", "")
                if email and "@" in email:
                    try:
                        username = email.split("@")[0]
                    except Exception as e:
                        logger.error(f"Error extracting username: {e}")
                
                # Check for organization membership
                if isinstance(user_data.get("current_organization"), dict):
                    organization_uri = user_data["current_organization"].get("uri", "")
        
        results = {
            "user_info": user_response,
            "user_uuid": user_uuid,
            "username": username,
            "organization_uri": organization_uri,
            "endpoints_tested": []
        }
        
        # Only proceed to test endpoints if we have a user UUID
        success_count = 0
        if user_uuid:
            # Basic URLs to test with different formats
            base_urls = [
                "https://api.calendly.com",
                "https://calendly.com/api"
            ]
            
            # EVENT TYPES ENDPOINTS - limit to fewer endpoints for initial testing
            event_types_endpoint_patterns = [
                # User-based endpoints - most common patterns first
                f"/users/{user_uuid}/event_types",
                f"/event_types?user={user_uuid}",
                f"/event_types?user=https://api.calendly.com/users/{user_uuid}",
                
                # Global endpoints
                f"/users/me/event_types"
            ]
            
            # SCHEDULED EVENTS ENDPOINTS - limit to fewer endpoints for initial testing
            scheduled_events_endpoint_patterns = [
                f"/users/{user_uuid}/scheduled_events",
                f"/scheduled_events?user={user_uuid}",
                f"/scheduled_events?user=https://api.calendly.com/users/{user_uuid}",
                
                # Global endpoints
                f"/users/me/scheduled_events"
            ]
            
            # Test event types endpoints
            results["event_types_tests"] = []
            for base_url in base_urls:
                for pattern in event_types_endpoint_patterns:
                    try:
                        full_url = f"{base_url}{pattern}"
                        logger.info(f"Testing event types endpoint: {full_url}")
                        
                        response = await test_direct_calendly_api(token=token, url=full_url)
                        
                        # Create a safe summary of the response content
                        response_summary = "No response data"
                        response_status = -1
                        response_success = False
                        
                        if response and hasattr(response, 'status_code'):
                            response_status = response.status_code
                        
                        if response and hasattr(response, 'success'):
                            response_success = response.success
                        
                        if response and hasattr(response, 'response_body'):
                            if response.response_body is not None:
                                try:
                                    if isinstance(response.response_body, str):
                                        response_summary = response.response_body[:200] + "..." if len(response.response_body) > 200 else response.response_body
                                    elif isinstance(response.response_body, dict):
                                        response_summary = str(dict(list(response.response_body.items())[:3])) + "..." 
                                    else:
                                        response_summary = str(response.response_body)[:200] + "..." if len(str(response.response_body)) > 200 else str(response.response_body)
                                except Exception as e:
                                    response_summary = f"Error creating summary: {str(e)}"
                        
                        if response_status == 200:
                            success_count += 1
                            
                        results["event_types_tests"].append({
                            "url": full_url,
                            "success": response_success,
                            "status": response_status,
                            "response_summary": response_summary
                        })
                    except Exception as e:
                        logger.error(f"Error testing endpoint {pattern}: {e}")
                        results["event_types_tests"].append({
                            "url": f"{base_url}{pattern}",
                            "success": False,
                            "status": 500,
                            "response_summary": f"Error: {str(e)}"
                        })
            
            # Test scheduled events endpoints - only if we didn't have too many event type successes
            if success_count < 3:
                results["scheduled_events_tests"] = []
                for base_url in base_urls:
                    for pattern in scheduled_events_endpoint_patterns:
                        try:
                            # Add time range parameters for scheduled events
                            now = datetime.now()
                            min_date = now.strftime("%Y-%m-%dT%H:%M:%S") 
                            params = f"min_start_time={min_date}"
                            full_url = f"{base_url}{pattern}?{params}"
                            logger.info(f"Testing scheduled events endpoint: {full_url}")
                            
                            response = await test_direct_calendly_api(token=token, url=full_url)
                            
                            # Create a safe summary of the response content
                            response_summary = "No response data"
                            response_status = -1
                            response_success = False
                            
                            if response and hasattr(response, 'status_code'):
                                response_status = response.status_code
                            
                            if response and hasattr(response, 'success'):
                                response_success = response.success
                            
                            if response and hasattr(response, 'response_body'):
                                if response.response_body is not None:
                                    try:
                                        if isinstance(response.response_body, str):
                                            response_summary = response.response_body[:200] + "..." if len(response.response_body) > 200 else response.response_body
                                        elif isinstance(response.response_body, dict):
                                            response_summary = str(dict(list(response.response_body.items())[:3])) + "..." 
                                        else:
                                            response_summary = str(response.response_body)[:200] + "..." if len(str(response.response_body)) > 200 else str(response.response_body)
                                    except Exception as e:
                                        response_summary = f"Error creating summary: {str(e)}"
                            
                            results["scheduled_events_tests"].append({
                                "url": full_url,
                                "success": response_success,
                                "status": response_status,
                                "response_summary": response_summary
                            })
                        except Exception as e:
                            logger.error(f"Error testing endpoint {pattern}: {e}")
                            results["scheduled_events_tests"].append({
                                "url": f"{base_url}{pattern}?{params if 'params' in locals() else ''}",
                                "success": False,
                                "status": 500,
                                "response_summary": f"Error: {str(e)}"
                            })
        
        # Add overall result
        results["status"] = "success"
        return results
    
    except Exception as e:
        logger.error(f"Global error in try_all_endpoints: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "An error occurred while testing Calendly endpoints"
        }
