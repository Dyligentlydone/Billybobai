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
    # Step 1: Get user info
    user_response = await get_user_info(token=token)
    
    # Extract user UUID and other useful information if successful
    user_uuid = None
    username = None
    organization_uri = None
    
    if user_response.success and "resource" in user_response.response_body:
        user_data = user_response.response_body["resource"]
        
        # Get user URI
        user_uri = user_data.get("uri")
        if user_uri:
            user_uuid = user_uri.split("/")[-1]
        
        # Extract username from email
        email = user_data.get("email")
        if email:
            username = email.split("@")[0]
        
        # Check for organization membership
        if "current_organization" in user_data:
            organization_uri = user_data["current_organization"].get("uri")
    
    results = {
        "user_info": user_response,
        "user_uuid": user_uuid,
        "username": username,
        "organization_uri": organization_uri,
        "endpoints_tested": []
    }
    
    # If we have a user UUID, try multiple endpoint formats
    if user_uuid:
        # Basic URLs to test with different formats
        base_urls = [
            "https://api.calendly.com",
            "https://calendly.com/api"
        ]
        
        # EVENT TYPES ENDPOINTS
        event_types_endpoint_patterns = [
            # User-based endpoints
            f"/users/{user_uuid}/event_types",
            f"/event_types?user={user_uuid}",
            f"/event_types?user=https://api.calendly.com/users/{user_uuid}",
            f"/v1/users/{user_uuid}/event_types",
            f"/v2/users/{user_uuid}/event_types",
            f"/scheduling_links?owner={user_uuid}",
            f"/scheduling_links?owner=https://api.calendly.com/users/{user_uuid}",
            
            # Organization-based endpoints (if available)
            f"/organizations/{user_uuid}/event_types",
            
            # Global endpoints
            f"/event_types",
            f"/users/me/event_types"
        ]
        
        # SCHEDULED EVENTS ENDPOINTS
        scheduled_events_endpoint_patterns = [
            f"/users/{user_uuid}/scheduled_events",
            f"/scheduled_events?user={user_uuid}",
            f"/scheduled_events?user=https://api.calendly.com/users/{user_uuid}",
            f"/v1/users/{user_uuid}/scheduled_events",
            f"/v2/users/{user_uuid}/scheduled_events",
            
            # Organization-based endpoints (if available)
            f"/organizations/{user_uuid}/scheduled_events",
            
            # Global endpoints
            f"/scheduled_events",
            f"/users/me/scheduled_events",
        ]
        
        # If we have a username, add username-based endpoints
        if username:
            event_types_endpoint_patterns.extend([
                f"/users/{username}/event_types",
                f"/event_types?user={username}"
            ])
            
            scheduled_events_endpoint_patterns.extend([
                f"/users/{username}/scheduled_events",
                f"/scheduled_events?user={username}"
            ])
        
        # If we have an organization URI, add organization-based endpoints
        if organization_uri:
            org_uuid = organization_uri.split("/")[-1]
            event_types_endpoint_patterns.extend([
                f"/organizations/{org_uuid}/event_types",
                f"/organizations/{org_uuid}/invitees"
            ])
            
            scheduled_events_endpoint_patterns.extend([
                f"/organizations/{org_uuid}/scheduled_events",
                f"/organizations/{org_uuid}/invitees"
            ])
        
        # Test event types endpoints
        results["event_types_tests"] = []
        for base_url in base_urls:
            for pattern in event_types_endpoint_patterns:
                full_url = f"{base_url}{pattern}"
                response = await test_direct_calendly_api(token=token, url=full_url)
                # Create a safe summary of the response content
                response_summary = None
                if response.success and response.response_body is not None:
                    if isinstance(response.response_body, str):
                        response_summary = response.response_body[:200] + "..." if len(response.response_body) > 200 else response.response_body
                    else:
                        response_summary = str(response.response_body)[:200] + "..." if len(str(response.response_body)) > 200 else str(response.response_body)
                
                results["event_types_tests"].append({
                    "url": full_url,
                    "success": response.success,
                    "status": response.status_code,
                    "response_summary": response_summary
                })
        
        # Test scheduled events endpoints
        results["scheduled_events_tests"] = []
        for base_url in base_urls:
            for pattern in scheduled_events_endpoint_patterns:
                # Add time range parameters for scheduled events
                params = "min_start_time=" + datetime.now().isoformat()
                full_url = f"{base_url}{pattern}?{params}"
                response = await test_direct_calendly_api(token=token, url=full_url)
                # Create a safe summary of the response content
                response_summary = None
                if response.success and response.response_body is not None:
                    if isinstance(response.response_body, str):
                        response_summary = response.response_body[:200] + "..." if len(response.response_body) > 200 else response.response_body
                    else:
                        response_summary = str(response.response_body)[:200] + "..." if len(str(response.response_body)) > 200 else str(response.response_body)
                
                results["scheduled_events_tests"].append({
                    "url": full_url,
                    "success": response.success,
                    "status": response.status_code,
                    "response_summary": response_summary
                })
    
    return results
