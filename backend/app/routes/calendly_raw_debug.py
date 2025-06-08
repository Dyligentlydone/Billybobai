from fastapi import APIRouter, Query
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
    
    # Extract user UUID if successful
    user_uuid = None
    if user_response.success and "resource" in user_response.response_body:
        user_uri = user_response.response_body["resource"].get("uri")
        if user_uri:
            user_uuid = user_uri.split("/")[-1]
    
    results = {
        "user_info": user_response,
        "endpoints_tested": []
    }
    
    # If we have a user UUID, try multiple endpoint formats
    if user_uuid:
        # List of endpoints to test
        endpoints_to_test = [
            f"https://api.calendly.com/users/{user_uuid}/event_types",
            f"https://api.calendly.com/event_types?user={user_uuid}",
            f"https://api.calendly.com/scheduling_links?owner={user_uuid}",
            f"https://api.calendly.com/scheduled_events?user=https://api.calendly.com/users/{user_uuid}",
            f"https://api.calendly.com/users/{user_uuid}/scheduled_events",
        ]
        
        # Test each endpoint
        for endpoint in endpoints_to_test:
            response = await test_direct_calendly_api(token=token, url=endpoint)
            results["endpoints_tested"].append({
                "url": endpoint,
                "success": response.success,
                "status": response.status_code,
                "response": response.response_body
            })
    
    return results
