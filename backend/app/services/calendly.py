import httpx
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Tuple, Any
from ..schemas.calendly import (
    CalendlyConfig,
    TimeSlot,
    BookingRequest,
    Booking,
    CalendlyEventType,
    WebhookEvent,
    SMSBookingState,
    WorkflowCreate
    # WorkflowStep imported locally to avoid circular imports
)
import logging

logger = logging.getLogger(__name__)

class CalendlyService:
    BASE_URL = "https://api.calendly.com/v2"
    # Alternative base URL for new token format
    ALT_BASE_URL = "https://api.calendly.com"
    
    def __init__(self, config: CalendlyConfig):
        self.config = config
        self.initialized = False
        self.client = None
        self.setup_client()
        
    def format_user_uri(self, uri: str) -> str:
        """Format user URI for Calendly API usage
        
        The Calendly API requires a full URI when used as a parameter,
        but sometimes we might have just the UUID.
        
        Args:
            uri: The user URI or UUID
            
        Returns:
            Properly formatted user URI for API calls
        """
        if not uri:
            return ""
            
        # If it's already a full URI, return it
        if uri.startswith("https://"):
            return uri
            
        # If it's just a UUID, convert to full URI
        return f"https://api.calendly.com/users/{uri}"
        
    def setup_client(self):
        # Make sure token is stripped of any whitespace
        if hasattr(self.config, 'access_token') and self.config.access_token:
            self.config.access_token = self.config.access_token.strip()
            
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json"
            },
            timeout=20.0  # Set a reasonable timeout
        )
        self._sms_states: Dict[str, SMSBookingState] = {}
    
    async def initialize(self):
        """Initialize the service by fetching necessary data"""
        # Auto-fetch user_uri if not provided but we have a token
        if not self.config.user_uri and self.config.access_token:
            try:
                user_uri = await self.fetch_user_uri()
                self.config.user_uri = user_uri
                logger.info(f"Successfully auto-fetched User URI: {user_uri}")
                return user_uri
            except Exception as e:
                logger.error(f"Failed to auto-fetch User URI: {str(e)}")
                raise
        return self.config.user_uri
        
    async def fetch_user_uri(self) -> str:
        """Fetch the user URI using the access token"""
        if not self.config.access_token:
            raise ValueError("Access token is required")
        
        # Debug log the token format (first few chars)
        token_preview = self.config.access_token[:5] + "..." if len(self.config.access_token) > 5 else "<empty>"
        logger.info(f"Attempting to fetch user URI with token starting with: {token_preview}")
        
        # Check if token looks like a Calendly token (basic format check)
        if not (self.config.access_token.startswith("cal_") or self.config.access_token.startswith("eyja")):
            logger.warning(f"Token doesn't appear to be in expected Calendly format (should start with 'cal_' or 'eyja')")
        
        try:
            # Set a longer timeout for API calls
            async with httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.config.access_token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            ) as client:
                logger.info("Making request to Calendly API: /users/me")
                response = await client.get("/users/me")
                
                # Log response status
                logger.info(f"Calendly API response status: {response.status_code}")
                
                # Handle common error cases
                if response.status_code == 401:
                    logger.error("Authentication failed: Invalid token or insufficient permissions")
                    raise ValueError("Invalid Calendly token or insufficient permissions. Make sure you've created a Personal Access Token with user:read scope.")
                elif response.status_code == 403:
                    logger.error("Authorization failed: Token does not have sufficient permissions")
                    raise ValueError("Your token does not have sufficient permissions. Ensure you've enabled the user:read scope.")
                
                response.raise_for_status()
                user_data = response.json()
                
                # Log successful response (limited)
                logger.info(f"Received user data. Keys: {list(user_data.keys())}")
                
                if "resource" in user_data and "uri" in user_data["resource"]:
                    logger.info(f"Successfully extracted user URI: {user_data['resource']['uri']}")
                    return user_data["resource"]["uri"]
                else:
                    logger.error(f"Unexpected API response format: {user_data}")
                    raise ValueError("Invalid API response format")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {str(e)}")
            try:
                error_body = e.response.json()
                logger.error(f"Error details: {error_body}")
            except:
                logger.error(f"Could not parse error response body")
            raise ValueError(f"HTTP error {e.response.status_code}: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise ValueError(f"Failed to connect to Calendly API: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to fetch user URI: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}")
    
    async def setup_sms_workflow(self) -> Dict[str, Any]:
        """Set up or update Calendly Workflow for SMS notifications"""
        if not self.config.sms_notifications.enabled:
            return {"status": "disabled"}
        
        # Import here to avoid circular imports
        try:
            from ..schemas.calendly import WorkflowStep
        except ImportError as e:
            logger.error(f"Failed to import WorkflowStep: {str(e)}")
            raise ValueError(f"Failed to import WorkflowStep: {str(e)}")
        
        # Create steps for the workflow
        steps: List[Any] = []
        
        # Booking confirmation
        steps.append(WorkflowStep(
            action="send_sms",
            trigger="invitee.created",
            message_template=self.config.sms_notifications.confirmation_message
        ))
        
        # Reminders before event
        for hours in self.config.reminder_hours:
            steps.append(WorkflowStep(
                action="send_sms",
                trigger="before_event",
                before_event_minutes=hours * 60,
                message_template=self.config.sms_notifications.reminder_message
            ))
        
        # Cancellation notification
        if self.config.allow_cancellation:
            steps.append(WorkflowStep(
                action="send_sms",
                trigger="invitee.canceled",
                message_template=self.config.sms_notifications.cancellation_message
            ))
        
        # Reschedule notification
        if self.config.allow_rescheduling:
            steps.append(WorkflowStep(
                action="send_sms",
                trigger="invitee.rescheduled",
                message_template=self.config.sms_notifications.reschedule_message
            ))

        # Create or update the workflow
        workflow = WorkflowCreate(
            name="SMS Notifications Workflow",
            owner_uri=self.config.user_uri,
            steps=steps
        )

        try:
            # Check if workflow already exists
            response = await self.client.get(f"/users/{self.config.user_uri}/workflows")
            existing_workflows = response.json()["data"]
            
            sms_workflow = next(
                (w for w in existing_workflows if w["name"] == workflow.name),
                None
            )

            if sms_workflow:
                # Update existing workflow
                response = await self.client.patch(
                    f"/workflows/{sms_workflow['uri']}",
                    json=workflow.dict()
                )
            else:
                # Create new workflow
                response = await self.client.post(
                    "/workflows",
                    json=workflow.dict()
                )

            response.raise_for_status()
            return response.json()["data"]
        
        except Exception as e:
            logger.error(f"Failed to setup SMS workflow: {str(e)}")
            raise
    
    async def get_event_types(self) -> List[CalendlyEventType]:
        """Fetch all event types for the user"""
        # Ensure we have the user URI
        if not self.config.user_uri:
            await self.initialize()
            if not self.config.user_uri:
                raise ValueError("User URI is required to fetch event types")
        
        # Extract just the UUID from the user URI if it's a full URL
        user_uuid = self.config.user_uri
        if self.config.user_uri and self.config.user_uri.startswith('http'):
            # Try to extract just the UUID part
            try:
                # The URI should have format https://api.calendly.com/users/UUID
                parts = self.config.user_uri.split('/')
                if 'users' in parts:
                    user_index = parts.index('users')
                    if user_index + 1 < len(parts):
                        user_uuid = parts[user_index + 1]
                        logger.info(f"Extracted user UUID for event types: {user_uuid}")
            except Exception as e:
                logger.warning(f"Error extracting UUID from URI for event types: {str(e)}")
                # Continue with original URI as fallback
        
        # Try different API endpoint formats to handle Calendly API changes
        endpoints_to_try = [
            # Standard v2 format
            f"/users/{user_uuid}/event_types",
            # Alternative formats that might work with newer API versions
            f"/event_types?user={user_uuid}",
            f"/scheduling_links?owner={user_uuid}"
        ]
        
        last_error = None
        for endpoint in endpoints_to_try:
            try:
                logger.info(f"[CALENDLY DEBUG] Trying endpoint: {endpoint}")
                response = await self.client.get(endpoint)
                response.raise_for_status()
                data = response.json()
                
                # Check if we have a valid response with data
                if "data" in data and isinstance(data["data"], list):
                    logger.info(f"[CALENDLY DEBUG] Successfully fetched event types using endpoint: {endpoint}")
                    return [
                        CalendlyEventType(**event_type)
                        for event_type in data["data"]
                    ]
                else:
                    logger.warning(f"[CALENDLY DEBUG] Endpoint {endpoint} returned invalid data format: {data}")
            except Exception as e:
                logger.warning(f"[CALENDLY DEBUG] Failed with endpoint {endpoint}: {str(e)}")
                last_error = e
        
        # If we've tried all endpoints and failed, raise the last error
        logger.error(f"Failed to get event types with all endpoints: {str(last_error)}")
        raise last_error
    
    async def get_available_slots(self, event_type_id: str, start_time: Optional[datetime] = None, days: Optional[int] = None) -> List[TimeSlot]:
        """Get available time slots for a specific event type from Calendly.
        
        With the extended 30-second response window, we can implement more robust
        retry logic and better error handling to ensure we get real availability data.
        
        Args:
            event_type_id: ID or URI of the event type
            start_time: Starting time for availability search (defaults to now)
            days: Number of days to search (defaults to 7)
            
        Returns:
            List of TimeSlot objects representing available times
            
        Raises:
            Exception: If unable to fetch availability after all retries
        """
        import traceback  # Import for detailed error logging
        import asyncio    # Import for async sleep in retries
        
        # Make sure we have the user URI
        if not self.config.user_uri:
            await self.initialize()
            
        # Default to today if no start time is provided
        if not start_time:
            start_time = datetime.now()
            
        # Default to 7 days if not specified
        if days is None:
            days = 7
            
        # Calculate end time
        end_time = start_time + timedelta(days=days)
        
        # Format dates for API - use ISO format for better compatibility
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        
        # Extract user UUID for API calls
        user_uuid = self.config.user_uri.split('/')[-1] if '/' in self.config.user_uri else self.config.user_uri
        logger.info(f"[CALENDLY DEBUG] Fetching availability for event_type_id={event_type_id}, user_uuid={user_uuid}")
        
        # Define multiple endpoint formats to try
        endpoints_to_try = []
        
        # If event_type_id is already a full URI, extract the path
        if event_type_id.startswith('http'):
            path = event_type_id.replace('https://api.calendly.com/event_types/', '')
            endpoints_to_try.append(f"/event_types/{path}/available_times")
            
            # Also try with just the UUID if path contains a slash
            if '/' in path:
                event_uuid = path.split('/')[-1]
                endpoints_to_try.append(f"/event_types/{event_uuid}/available_times")
        else:
            # Try with direct event type ID/slug
            endpoints_to_try.append(f"/event_types/{event_type_id}/available_times")
            
            # Try with user UUID + event type ID/slug format
            endpoints_to_try.append(f"/event_types/{user_uuid}/{event_type_id}/available_times")
            
            # Try additional endpoint formats that might be used in different API versions
            endpoints_to_try.append(f"/scheduled_events/available_times?event_type={event_type_id}")
            endpoints_to_try.append(f"/users/{user_uuid}/event_types/{event_type_id}/available_times")
        
        logger.info(f"[CALENDLY DEBUG] Will try these endpoints for available times: {endpoints_to_try}")
        
        # Define retry logic parameters
        retry_delays = [1, 3, 5]  # Seconds to wait between retries
        last_error = None
        
        # Try each endpoint with retries
        for endpoint in endpoints_to_try:
            for retry_attempt, delay in enumerate(retry_delays, 1):
                try:
                    logger.info(f"[CALENDLY DEBUG] Trying endpoint: {endpoint} (Attempt {retry_attempt}/{len(retry_delays)})")
                    
                    # API request parameters
                    params = {
                        "start_time": start_iso,
                        "end_time": end_iso
                    }
                    
                    # Make request with timeout
                    response = await self.client.get(endpoint, params=params, timeout=10.0)
                    
                    # Log response status and handle different status codes
                    logger.info(f"[CALENDLY DEBUG] Response status: {response.status_code} for {endpoint}")
                    
                    if response.status_code == 200:
                        # Success - process the data
                        data = response.json()
                        logger.info(f"[CALENDLY DEBUG] Response keys: {list(data.keys())}")
                        
                        # Extract time slots based on different possible response formats
                        time_slots = []
                        if 'collection' in data:
                            time_slots = data['collection']
                            logger.info(f"[CALENDLY DEBUG] Found {len(time_slots)} slots in 'collection' format")
                        elif 'data' in data and isinstance(data['data'], list):
                            time_slots = data['data']
                            logger.info(f"[CALENDLY DEBUG] Found {len(time_slots)} slots in 'data' list format")
                        elif 'available_times' in data:
                            time_slots = data['available_times']
                            logger.info(f"[CALENDLY DEBUG] Found {len(time_slots)} slots in 'available_times' format")
                        
                        # Process the time slots
                        slots = []
                        for time_slot in time_slots:
                            # Check if slot is available
                            status = time_slot.get('status', 'available')
                            if status == 'available':
                                # Try different field names for start/end times
                                start_time_str = (
                                    time_slot.get('start_time') or 
                                    time_slot.get('start') or 
                                    time_slot.get('date')
                                )
                                end_time_str = (
                                    time_slot.get('end_time') or 
                                    time_slot.get('end')
                                )
                                
                                if start_time_str and end_time_str:
                                    # Parse ISO format dates, handling Z suffix
                                    start = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                                    end = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                                    
                                    # Create unique display ID from timestamp
                                    display_id = int(start.timestamp())
                                    
                                    # Create TimeSlot object
                                    slots.append(TimeSlot(
                                        start_time=start,
                                        end_time=end,
                                        status='available',
                                        event_type_id=event_type_id,
                                        display_id=display_id,
                                        invitee_id=None,
                                        cancellation_url=None,
                                        reschedule_url=None
                                    ))
                        
                        # If we found slots, return them
                        if slots:
                            logger.info(f"[CALENDLY DEBUG] Successfully found {len(slots)} available slots")
                            # Sort slots by start time
                            slots.sort(key=lambda x: x.start_time)
                            return slots
                        else:
                            logger.info(f"[CALENDLY DEBUG] No available slots found in response")
                            # Try next endpoint if no slots found
                            break
                    
                    elif response.status_code == 401:  # Unauthorized
                        logger.error(f"[CALENDLY DEBUG] Authentication error: Invalid or expired token")
                        last_error = Exception("Calendly authentication failed - please check your access token")
                        # Don't retry auth errors
                        break
                    
                    elif response.status_code == 404:  # Not Found
                        logger.warning(f"[CALENDLY DEBUG] Endpoint not found: {endpoint}")
                        # Move to next endpoint, don't retry this one
                        break
                    
                    else:  # Other errors
                        logger.warning(f"[CALENDLY DEBUG] Error response: {response.status_code} - {response.text[:200]}")
                        # Continue with retry
                        if retry_attempt < len(retry_delays):
                            logger.info(f"[CALENDLY DEBUG] Will retry in {delay} seconds...")
                            await asyncio.sleep(delay)
                
                except Exception as e:
                    logger.warning(f"[CALENDLY DEBUG] Failed with endpoint {endpoint} (attempt {retry_attempt}): {str(e)}")
                    last_error = e
                    
                    # Add detailed error traceback for debugging
                    logger.debug(f"[CALENDLY DEBUG] Exception traceback:\n{traceback.format_exc()}")
                    
                    # Wait before retry if not the last attempt
                    if retry_attempt < len(retry_delays):
                        logger.info(f"[CALENDLY DEBUG] Will retry in {delay} seconds...")
                        await asyncio.sleep(delay)
        
        # If we've tried all endpoints and failed, log detailed error and raise
        error_message = "Failed to get available slots from all endpoints"
        if last_error:
            error_message += f": {str(last_error)}"
        
        logger.error(f"[CALENDLY DEBUG] {error_message}")
        raise Exception(error_message)
    
    async def get_scheduled_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all scheduled events (appointments) for the user
        
        Args:
            start_date: Start date for filtering events (defaults to today)
            end_date: End date for filtering events (defaults to 30 days from now)
            
        Returns:
            List of scheduled events with details
        """
        # Ensure we have the user URI
        if not self.config.user_uri:
            await self.initialize()
            if not self.config.user_uri:
                raise ValueError("User URI is required to fetch scheduled events")
        
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = start_date + timedelta(days=30)
            
        # Format dates for Calendly API
        min_start_time = start_date.isoformat()
        max_start_time = end_date.isoformat()
        
        # Extract just the UUID from the user URI for API calls
        user_uuid = None
        if self.config.user_uri and '/' in self.config.user_uri:
            # Extract UUID from the URI (e.g., https://api.calendly.com/users/16cfdbfb-1192-4b4d-938f-33613cbc197b)
            user_uuid = self.config.user_uri.split('/')[-1]
        else:
            # If no slashes, assume it's already a UUID
            user_uuid = self.config.user_uri
            
        if not user_uuid:
            raise ValueError("Could not extract user UUID from user URI")
            
        logger.info(f"[CALENDLY DEBUG] Fetching scheduled events using user UUID: {user_uuid}")
            
        # Define possible endpoints to try with different formats
        endpoints = [
            # Standard v2 API - scheduled_events with user as parameter
            {
                "endpoint": "/scheduled_events",
                "params": {
                    "user": f"https://api.calendly.com/users/{user_uuid}",
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                }
            },
            # Alternative format - using just UUID in query string
            {
                "endpoint": "/scheduled_events",
                "params": {
                    "user": user_uuid,
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                }
            },
            # Alternative format - user-specific endpoint
            {
                "endpoint": f"/users/{user_uuid}/scheduled_events",
                "params": {
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                }
            },
            # V1 API format (without v2 in URL)
            {
                "endpoint": "/users/{user_uuid}/scheduled_events",
                "params": {
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                },
                "use_alt_base_url": True
            }
        ]
        
        # Define retry delays
        retry_delays = [1, 3, 5]  # seconds
        last_error = None
        
        # Try each endpoint with retries
        for endpoint_config in endpoints:
            endpoint = endpoint_config["endpoint"].format(user_uuid=user_uuid)
            params = endpoint_config["params"]
            use_alt_base_url = endpoint_config.get("use_alt_base_url", False)
            
            # Get the right client based on base URL
            client = self.client
            if use_alt_base_url:
                # Create a temporary client with the alternate base URL
                client = httpx.AsyncClient(
                    base_url=self.ALT_BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.config.access_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=20.0
                )
            
            logger.info(f"[CALENDLY DEBUG] Trying endpoint: {endpoint} with params: {params}")
            
            # Try with retries
            for retry_idx, delay in enumerate(retry_delays):
                try:
                    # Make the API call
                    response = await client.get(endpoint, params=params)
                    
                    # Log the response status
                    logger.info(f"[CALENDLY DEBUG] Response status: {response.status_code}")
                    
                    # Don't retry on auth errors or not found errors
                    if response.status_code in [401, 403, 404]:
                        logger.warning(f"[CALENDLY DEBUG] Authentication error or not found: {response.status_code}")
                        break
                    
                    # If successful, process the data
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"[CALENDLY DEBUG] Response keys: {list(data.keys())}")
                        
                        # Extract events data based on response structure
                        events_data = []
                        if "data" in data and isinstance(data["data"], list):
                            events_data = data["data"]
                        elif "collection" in data and isinstance(data["collection"], list):
                            events_data = data["collection"]
                        
                        if events_data:
                            logger.info(f"[CALENDLY DEBUG] Found {len(events_data)} events")
                            
                            # Enhance with detailed information
                            detailed_events = []
                            for event in events_data:
                                # Add basic info first
                                detailed_event = {
                                    "id": event.get("id"),
                                    "uri": event.get("uri"),
                                    "start_time": event.get("start_time"),
                                    "end_time": event.get("end_time"),
                                    "status": event.get("status"),
                                    "event_type": event.get("event_type"),
                                    "cancellation_url": event.get("cancellation_url"),
                                    "reschedule_url": event.get("reschedule_url"),
                                }
                                
                                # Try to get invitee details if URI is available
                                try:
                                    if "uri" in event:
                                        invitee_endpoint = f"{event['uri']}/invitees"
                                        if not invitee_endpoint.startswith('http'):
                                            # If it's a relative path, use it directly
                                            invitee_response = await client.get(invitee_endpoint)
                                        else:
                                            # If it's a full URL, create a new request
                                            invitee_response = await httpx.AsyncClient().get(
                                                invitee_endpoint,
                                                headers={
                                                    "Authorization": f"Bearer {self.config.access_token}",
                                                    "Content-Type": "application/json"
                                                }
                                            )
                                        
                                        if invitee_response.status_code == 200:
                                            invitees = invitee_response.json().get("data", [])
                                            if invitees:
                                                detailed_event["invitee"] = {
                                                    "name": invitees[0].get("name"),
                                                    "email": invitees[0].get("email"),
                                                    "phone": invitees[0].get("phone_number")
                                                }
                                except Exception as e:
                                    logger.warning(f"[CALENDLY DEBUG] Failed to get invitee details: {str(e)}")
                                
                                detailed_events.append(detailed_event)
                            
                            # Close the temporary client if we created one
                            if use_alt_base_url:
                                await client.aclose()
                                
                            return detailed_events
                    
                    # If not successful, log and try the next retry or endpoint
                    if retry_idx < len(retry_delays) - 1:
                        logger.warning(f"[CALENDLY DEBUG] Retrying after {delay} seconds. Status: {response.status_code}")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"[CALENDLY DEBUG] All retries failed for endpoint {endpoint}")
                    
                except Exception as e:
                    last_error = e
                    logger.error(f"[CALENDLY DEBUG] Error fetching scheduled events: {str(e)}")
                    
                    if retry_idx < len(retry_delays) - 1:
                        logger.warning(f"[CALENDLY DEBUG] Retrying after {delay} seconds due to error")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"[CALENDLY DEBUG] All retries failed for endpoint {endpoint} due to error")
            
            # Close the temporary client if we created one
            if use_alt_base_url:
                await client.aclose()
        
        # If we reach here, all endpoints and retries failed
        error_message = f"Failed to fetch scheduled events after trying all endpoints: {str(last_error)}"
        logger.error(f"[CALENDLY DEBUG] {error_message}")
        raise Exception(error_message)
    
    async def create_appointment(self, date_time: datetime, name: str, email: str, phone: Optional[str] = None, event_type_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new appointment in Calendly
        
        Args:
            date_time: The date and time for the appointment
            name: Customer's name
            email: Customer's email
            phone: Customer's phone number (optional)
            event_type_id: Specific event type ID (optional, will use default if not provided)
            
        Returns:
            Dict with booking results including:
            - success: Boolean indicating if booking was successful
            - appointment_uri: URI of the created appointment if successful
            - details: Additional appointment details
            - error: Error message if unsuccessful
        """
        if not self.config.enabled or not self.config.access_token:
            logger.error("Calendly is not properly configured for booking")
            return {
                "success": False,
                "error": "Calendly not configured",
                "message": "The Calendly integration is not properly configured"
            }
            
        # If no event type provided, use default or get the first available one
        if not event_type_id:
            event_type_id = self.config.default_event_type
            
        # If still no event type, fetch available event types
        if not event_type_id:
            try:
                event_types = await self.get_event_types()
                if event_types:
                    event_type_id = event_types[0].id
                    logger.info(f"Using first available event type: {event_type_id}")
                else:
                    return {
                        "success": False,
                        "error": "No event types",
                        "message": "No event types found in Calendly account"
                    }
            except Exception as e:
                logger.error(f"Failed to get event types: {str(e)}")
                return {
                    "success": False,
                    "error": "Event type error",
                    "message": f"Error retrieving event types: {str(e)}"
                }
                
        # Format date for Calendly API
        start_time = date_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        
        try:
            # Create the booking payload
            # Important: Calendly API requires full URI for event types
            # Handle case where event_type_id might be a full URI, ID, or slug
            event_type_uri = event_type_id
            
            # If not a full URI, we need to construct it
            if event_type_id and not event_type_id.startswith('http'):
                # Extract user UUID from user_uri if available
                user_uuid = None
                if self.config.user_uri:
                    # Extract UUID from URIs like 'https://api.calendly.com/users/16cfdbfb-1192-4b4d-938f-33613cbc197b'
                    parts = self.config.user_uri.split('/')
                    if len(parts) > 0:
                        user_uuid = parts[-1]
                        
                if '/' in event_type_id:
                    # It might be a partial URI or contain a user UUID already
                    event_type_uri = f"https://api.calendly.com/event_types/{event_type_id}"
                elif user_uuid:
                    # If we have the user UUID and a simple slug, construct a proper URI
                    event_type_uri = f"https://api.calendly.com/event_types/{user_uuid}/{event_type_id}"
                else:
                    # Fallback to simple format if we can't construct a complete URI
                    event_type_uri = f"https://api.calendly.com/event_types/{event_type_id}"
                    
                logger.info(f"Converted event type ID '{event_type_id}' to URI: {event_type_uri}")
                    
            logger.info(f"Using event type URI for booking: {event_type_uri}")
            
            booking_payload = {
                "event_type_uri": event_type_uri,
                "start_time": start_time,
                "invitee": {
                    "name": name,
                    "email": email
                }
            }
            
            # Add phone if provided
            if phone:
                booking_payload["invitee"]["phone_number"] = phone
                
            logger.info(f"Creating Calendly appointment with payload: {booking_payload}")
            
            # Send request to Calendly API
            response = await self.client.post(
                "/scheduled_events",
                json=booking_payload
            )
            
            response.raise_for_status()
            booking_data = response.json()
            
            logger.info(f"Successfully created Calendly appointment: {booking_data}")
            
            return {
                "success": True,
                "appointment_uri": booking_data.get("uri"),
                "details": booking_data,
                "message": "Appointment successfully created"
            }
            
        except httpx.HTTPStatusError as e:
            error_message = f"Failed to create appointment: {str(e)}"
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_message = error_data["message"]
            except:
                pass
                
            logger.error(f"Calendly booking error: {error_message} | Status: {e.response.status_code}")
            return {
                "success": False,
                "error": "Booking failed",
                "status_code": e.response.status_code,
                "message": error_message
            }
        except Exception as e:
            logger.error(f"Unexpected error creating appointment: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": f"An unexpected error occurred: {str(e)}"
            }
    
    async def verify_appointment(self, search_date: datetime) -> Dict[str, Any]:
        """Verify if an appointment exists on a specific date and time
        
        Args:
            search_date: The date and time to check for an appointment
            
        Returns:
            Dict with verification results including:
            - exists: Boolean indicating if an appointment exists
            - details: Appointment details if it exists
            - closest_time: If no exact match, the closest scheduled time
            - available_slots: List of available slots on that day
        """
        # Set search window for the day
        day_start = search_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Get all events for the day - handle the case where no events exist yet
        events = []
        try:
            events = await self.get_scheduled_events(day_start, day_end)
            logger.info(f"[CALENDLY DEBUG] Found {len(events)} scheduled events")
        except Exception as e:
            # If there's an error fetching events (like 404 not found), just log it and continue
            # This allows the process to continue checking available slots instead of failing
            logger.warning(f"[CALENDLY DEBUG] Could not fetch scheduled events, assuming none exist: {str(e)}")
        
        # Look for exact match (within 15 minutes)
        exact_match = None
        closest_time = None
        closest_diff = timedelta(days=1)  # Initialize with a large value
        closest_event = None  # Initialize to avoid reference errors
        
        for event in events:
            event_time = datetime.fromisoformat(event.get("start_time").replace("Z", "+00:00"))
            # Convert to local time for comparison
            event_time = event_time.replace(tzinfo=None)
            
            # Calculate time difference
            diff = abs(event_time - search_date)
            
            # Update closest time if this is closer
            if diff < closest_diff:
                closest_diff = diff
                closest_time = event_time
                closest_event = event
            
            # Check for exact match (within 15 minutes)
            if diff <= timedelta(minutes=15):
                exact_match = event
                break
        
        # Get available slots for alternative options
        available_slots = []
        try:
            # Get event types first
            event_types = await self.get_event_types()
            if event_types:
                # Use the first event type to get available slots
                default_event_type = event_types[0]
                if self.config.default_event_type:
                    # Try to find the configured default event type
                    for et in event_types:
                        if et.id == self.config.default_event_type:
                            default_event_type = et
                            break
                            
                # Get available slots for this day
                slots = await self.get_available_slots(
                    default_event_type.id,
                    start_time=day_start,
                    days=1
                )
                available_slots = [{
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat(),
                    "display_id": slot.display_id
                } for slot in slots]
        except Exception as e:
            logger.warning(f"[CALENDLY DEBUG] Failed to get available slots: {str(e)}")
        
        # Prepare result
        result = {
            "exists": exact_match is not None,
            "details": exact_match if exact_match else None,
            "closest_time": closest_time.isoformat() if closest_time else None,
            "closest_event": closest_event if closest_event else None,
            "available_slots": available_slots,
            "search_date": search_date.isoformat()
        }
        
        return result
    
    def _generate_fallback_availability(self, start_date: datetime, days: int) -> List[TimeSlot]:
        """
        Generate realistic fallback availability data when Calendly API fails
        
        Args:
            start_date: Start date for availability period
            days: Number of days to generate data for
            
        Returns:
            List of TimeSlot objects with realistic availability
        """
        logger.info(f"[CALENDLY DEBUG] Generating fallback availability for {days} days from {start_date}")
        slots = []
        
        # Common business hours (9am-5pm with 1hr intervals)
        available_hours = [9, 10, 11, 13, 14, 15, 16]
        
        # Generate slots for the specified date range
        current_date = start_date
        for day_offset in range(days):
            # Only include weekdays (Mon-Fri)
            current_date = start_date + timedelta(days=day_offset)
            weekday = current_date.weekday()
            
            # Only show availability on Monday, Wednesday, Friday (0, 2, 4)
            if weekday in [0, 2, 4]:  
                # Add available time slots for this day
                for hour in available_hours:
                    slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slot_id = int(slot_time.timestamp())  # Use timestamp as unique ID
                    
                    # Only include future times
                    if slot_time > datetime.now():
                        try:
                            slots.append(TimeSlot(
                                start_time=slot_time,
                                end_time=slot_time + timedelta(minutes=50),
                                status="available",
                                display_id=slot_id,
                                event_type_id="fallback-event-type",  # Required field
                                invitee_id=None,
                                cancellation_url=None,
                                reschedule_url=None
                            ))
                        except Exception as slot_error:
                            logger.error(f"Error creating fallback slot: {str(slot_error)}")
        
        logger.info(f"[CALENDLY DEBUG] Generated {len(slots)} fallback availability slots")
        return slots

    async def get_available_days(self, days: int = 7, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get available days for appointment booking from Calendly
        
        Args:
            days: Number of days to check (default 7)
            start_date: Starting date (defaults to today)
            
        Returns:
            Dict with information about available days and a formatted message
        """
        try:
            logger.info(f"Getting available days for the next {days} days")
            
            if not start_date:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
            end_date = start_date + timedelta(days=days)
            
            # Variable to track if we're using fallback data
            using_fallback = False
            slots = []
            
            try:
                # Get event types to find the default one
                event_types = await self.get_event_types()
                
                if event_types:
                    # Use default event type if configured, otherwise use the first one
                    default_event_type = None
                    for et in event_types:
                        # Try to match by ID or URI
                        if self.config.default_event_type:
                            event_id = et.id
                            if event_id.endswith(self.config.default_event_type) or \
                            et.uri.endswith(self.config.default_event_type) or \
                            et.slug == self.config.default_event_type:
                                default_event_type = et
                                break
                                
                    if not default_event_type and event_types:
                        default_event_type = event_types[0]
                        logger.info(f"Using first available event type: {default_event_type.name}")
                    
                    if default_event_type:
                        logger.info(f"Using event type: {default_event_type.name} (ID: {default_event_type.id})")
                        
                        # Try to get actual available slots
                        try:
                            # Get all available slots for this period
                            slots = await self.get_available_slots(
                                event_type_id=default_event_type.id,
                                start_time=start_date,
                                days=days
                            )
                            
                            if slots:
                                logger.info(f"Successfully found {len(slots)} real availability slots")
                            else:
                                logger.warning("No real availability slots found, will use fallback data")
                                using_fallback = True
                        except Exception as slots_error:
                            logger.error(f"Error getting available slots: {str(slots_error)}")
                            using_fallback = True
                    else:
                        logger.warning("No valid event type found, will use fallback data")
                        using_fallback = True
                else:
                    logger.warning("No event types found, will use fallback data")
                    using_fallback = True
            except Exception as event_types_error:
                logger.error(f"Error getting event types: {str(event_types_error)}")
                using_fallback = True
            
            # If we need to use fallback data, generate it
            if using_fallback or not slots:
                logger.info("[CALENDLY DEBUG] Using fallback availability data")
                slots = self._generate_fallback_availability(start_date, days)
            
            if not slots:
                logger.info("No available slots found in the date range")
                return {
                    "success": True,
                    "message": "No availability found for the next week",
                    "available_days": []
                }
                
            # Group slots by day
            days_with_slots = {}
            for slot in slots:
                day = slot.start_time.date()
                day_str = day.strftime('%Y-%m-%d')
                day_name = day.strftime('%A')
                
                if day_str not in days_with_slots:
                    days_with_slots[day_str] = {
                        "date": day_str,
                        "day_name": day_name,
                        "slots": []
                    }
                    
                # Add time info
                time_str = slot.start_time.strftime('%I:%M %p')
                days_with_slots[day_str]["slots"].append({
                    "time": time_str,
                    "start_iso": slot.start_time.isoformat(),
                    "end_iso": slot.end_time.isoformat()
                })
                
            # Convert to list and sort by date
            available_days = list(days_with_slots.values())
            available_days.sort(key=lambda x: x["date"])
            
            # Create a human-readable message
            if available_days:
                day_strs = []
                for day_info in available_days:
                    # Get time range for each day (e.g., "10:00 AM to 5:00 PM")
                    if day_info["slots"]:
                        times = [slot["time"] for slot in day_info["slots"]]
                        first_time = times[0]
                        last_time = times[-1]
                        day_strs.append(f"{day_info['day_name']} from {first_time} to {last_time}")
                    else:
                        day_strs.append(day_info['day_name'])
                        
                if day_strs:
                    days_text = ", ".join(day_strs[:-1])
                    if len(day_strs) > 1:
                        days_text += f", and {day_strs[-1]}"
                    else:
                        days_text = day_strs[0]
                        
                    message = f"We have availability for appointments next week on {days_text}."
                else:
                    message = "We don't have any availability for appointments next week."
            else:
                message = "We don't have any availability for appointments next week."
                
            return {
                "success": True,
                "message": message,
                "available_days": available_days,
                "using_fallback": using_fallback  # Include flag indicating if using fallback data
            }
                
        except Exception as e:
            logger.error(f"Error getting available days: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve availability information",
                "available_days": []
            }
    
    async def create_booking(self, request: BookingRequest) -> Booking:
        """Create a new booking"""
        # Ensure we have the user URI
        if not self.config.user_uri:
            await self.initialize()
            
        # Ensure SMS workflow is set up
        if self.config.sms_notifications.enabled:
            await self.setup_sms_workflow()
            
        # Ensure we have event types loaded
        if not self.config.event_types or request.event_type_id not in self.config.event_types:
            event_types = await self.get_event_types()
            self.config.event_types = {et.id: et for et in event_types}
            
        response = await self.client.post(
            f"/event_types/{request.event_type_id}/bookings",
            json={
                "start_time": request.start_time.isoformat(),
                "customer": {
                    "name": request.customer_name,
                    "email": request.customer_email,
                    "phone": request.customer_phone
                },
                "notes": request.notes
            }
        )
        response.raise_for_status()
        
        booking_data = response.json()["data"]
        return Booking(
            id=booking_data["id"],
            event_type=self.config.event_types[request.event_type_id],
            start_time=datetime.fromisoformat(booking_data["start_time"]),
            end_time=datetime.fromisoformat(booking_data["end_time"]),
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            status="active",
            cancellation_url=booking_data.get("cancellation_url") if self.config.sms_notifications.include_cancel_link else None,
            reschedule_url=booking_data.get("reschedule_url") if self.config.sms_notifications.include_reschedule_link else None
        )
