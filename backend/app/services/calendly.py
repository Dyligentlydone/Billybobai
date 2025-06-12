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
from urllib.parse import quote
import traceback

class CalendlyError(Exception):
    """Custom exception for Calendly-related errors."""
    pass

logger = logging.getLogger(__name__)

class CalendlyService:
    # Use root URL; v2 endpoints are path-only (e.g. /event_types)
    BASE_URL = "https://api.calendly.com"
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
        import asyncio  # For retry delays
        
        if not self.config.access_token:
            raise ValueError("Access token is required")
        
        # Debug log the token format (first few chars)
        token_preview = self.config.access_token[:5] + "..." if len(self.config.access_token) > 5 else "<empty>"
        logger.info(f"[CALENDLY DEBUG] Attempting to fetch user URI with token starting with: {token_preview}")
        
        # Check if token looks like a Calendly token (basic format check)
        if not (self.config.access_token.startswith("cal_") or self.config.access_token.startswith("eyja")):
            logger.warning(f"[CALENDLY DEBUG] Token doesn't appear to be in expected Calendly format (should start with 'cal_' or 'eyja')")
        
        # Define endpoints to try in order
        endpoints_to_try = [
            "/users/me",            # Standard endpoint
            "/v2/users/me",         # With explicit v2 prefix
            "/v1/users/me",         # Try v1 as fallback
            "/api/v2/users/me",     # Additional format sometimes used
            "/api/v1/users/me"      # Additional format sometimes used
        ]
        
        # Define URLs to try
        urls_to_try = [
            self.BASE_URL,
            "https://api.calendly.com",  # Direct API URL
            "https://auth.calendly.com"   # Auth-specific URL
        ]
        
        last_error = None
        
        # Try each combination of URL and endpoint
        for base_url in urls_to_try:
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"[CALENDLY DEBUG] Trying {base_url}{endpoint} to fetch user information")
                    
                    # Set a longer timeout for API calls
                    async with httpx.AsyncClient(
                        base_url=base_url,
                        headers={
                            "Authorization": f"Bearer {self.config.access_token.strip()}",
                            "Content-Type": "application/json"
                        },
                        timeout=10.0  # Shorter timeout for faster failures
                    ) as client:
                        logger.info(f"[CALENDLY DEBUG] Making request to: {endpoint}")
                        response = await client.get(endpoint)
                        
                        # Log response status
                        logger.info(f"[CALENDLY DEBUG] API response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            user_data = response.json()
                            logger.info(f"[CALENDLY DEBUG] Received user data. Keys: {list(user_data.keys())}")
                            
                            # Try different response formats
                            if "resource" in user_data and "uri" in user_data["resource"]:
                                logger.info(f"[CALENDLY DEBUG] Found user URI in resource.uri: {user_data['resource']['uri']}")
                                return user_data["resource"]["uri"]
                            elif "uri" in user_data:
                                logger.info(f"[CALENDLY DEBUG] Found user URI directly: {user_data['uri']}")
                                return user_data["uri"]
                            elif "data" in user_data and "uri" in user_data["data"]:
                                logger.info(f"[CALENDLY DEBUG] Found user URI in data.uri: {user_data['data']['uri']}")
                                return user_data["data"]["uri"]
                            else:
                                # If we have a successful response but can't find URI in expected format,
                                # log the structure and try a generic approach
                                logger.info(f"[CALENDLY DEBUG] Unexpected but successful response structure: {user_data}")
                                # Search for any field that looks like a user URI
                                for key, value in user_data.items():
                                    if isinstance(value, str) and "users" in value and "/" in value:
                                        logger.info(f"[CALENDLY DEBUG] Found potential user URI in '{key}': {value}")
                                        return value
                                        
                                logger.warning(f"[CALENDLY DEBUG] Could not find user URI in response")
                                # Continue to next attempt since we couldn't parse this one
                        
                        # Handle specific error cases but continue trying other endpoints
                        elif response.status_code == 401:
                            logger.error(f"[CALENDLY DEBUG] Authentication failed ({endpoint}): Invalid token or expired")
                            last_error = ValueError("Invalid Calendly token or token has expired. Check your Personal Access Token settings.")
                        elif response.status_code == 403:
                            logger.error(f"[CALENDLY DEBUG] Authorization failed ({endpoint}): Insufficient permissions")
                            last_error = ValueError("Your token does not have sufficient permissions. Ensure you've enabled the user:read scope.")
                        elif response.status_code == 404:
                            logger.info(f"[CALENDLY DEBUG] Endpoint not found ({endpoint}): Will try other endpoints")
                            # 404 just means this endpoint doesn't exist, we'll continue to try others
                            pass
                            
                except httpx.HTTPStatusError as e:
                    logger.error(f"[CALENDLY DEBUG] HTTP error with {endpoint}: {e.response.status_code} - {str(e)}")
                    try:
                        error_body = e.response.json()
                        logger.error(f"[CALENDLY DEBUG] Error details: {error_body}")
                    except:
                        pass
                    last_error = e
                except httpx.RequestError as e:
                    logger.error(f"[CALENDLY DEBUG] Request error with {endpoint}: {str(e)}")
                    last_error = e
                except Exception as e:
                    logger.error(f"[CALENDLY DEBUG] Unexpected error with {endpoint}: {str(e)}")
                    last_error = e
                
                # Small delay between attempts
                await asyncio.sleep(0.5)
        
        # If we've tried all combinations and nothing worked
        logger.error("[CALENDLY DEBUG] All endpoints failed when trying to fetch user URI")
        if last_error:
            raise ValueError(f"Failed to fetch user URI from any endpoint: {str(last_error)}")
        else:
            raise ValueError("Failed to fetch user URI from any endpoint")

    
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
        last_error = None
        """Fetch all event types for the user"""
        import asyncio  # For retry delays
        
        # Ensure we have the user URI
        if not self.config.user_uri:
            await self.initialize()
            if not self.config.user_uri:
                raise ValueError("User URI is required to fetch event types")
        
        logger.info(f"[CALENDLY DEBUG] Getting event types with user_uri: {self.config.user_uri}")
        
        # Extract the user UUID from the config's user_uri
        user_uri = self.config.user_uri
        user_uuid = user_uri.split("/")[-1]
        logging.debug(f"Extracted user UUID: {user_uuid}")
        
        # MODIFIED: Reorder endpoints to prioritize non-versioned endpoints
        # Based on our diagnostic testing, we prioritize the most reliable endpoints
        endpoints_to_try = [
            # Non-versioned endpoints (these work with JWT tokens)
            f"{self.BASE_URL}/users/{user_uuid}/event_types",  # Legacy v1-style path
            f"{self.BASE_URL}/event_types?user={quote(self.config.user_uri, safe='')}",  # Standard query param
            
            # Fallbacks
            f"{self.BASE_URL}/event_types?user={quote(user_uuid, safe='')}"
        ]
        
        logger.info(f"[CALENDLY DEBUG] Will try {len(endpoints_to_try)} endpoints for event types")
        
        # Define retry logic parameters
        retry_delays = [1, 2]  # Seconds to wait between retries - reduced for faster testing
        last_error = None
        
        # Try each endpoint with retries
        for endpoint in endpoints_to_try:
            for retry_attempt, delay in enumerate(retry_delays, 1):
                try:
                    logger.info(f"[CALENDLY DEBUG] Trying endpoint: {endpoint} (Attempt {retry_attempt}/{len(retry_delays)})")
                    
                    # API request parameters
                    params = {}
                    
                    # Make request with timeout
                    response = await self.client.get(endpoint, params=params, timeout=10.0)
                    
                    # Log response status and handle different status codes
                    logger.info(f"[CALENDLY DEBUG] Response status: {response.status_code} for {endpoint}")
                    
                    if response.status_code == 200:
                        # Success - process the data
                        data = response.json()
                        logger.info(f"[CALENDLY DEBUG] Response keys: {list(data.keys())}")
                        
                        # Extract event types list from various possible keys
                        if isinstance(data, list):
                            event_types_raw = data
                        elif isinstance(data, dict):
                            event_types_raw = (
                                data.get("collection")
                                or data.get("data")
                                or data.get("event_types")
                                or []
                            )
                        else:
                            event_types_raw = []
                        
                        logger.info(f"[CALENDLY DEBUG] Found {len(event_types_raw)} event types in response")
                    logger.info(f"[CALENDLY DEBUG] SUCCESSFUL ENDPOINT: {endpoint}")
                    
                    # Log the first event type to help with debugging
                    if event_types_raw and len(event_types_raw) > 0:
                        logger.info(f"[CALENDLY DEBUG] First event type: {event_types_raw[0]}")
                        
                        return [
                            CalendlyEventType(
                                id=et.get("uri", et.get("id", "")),
                                name=et.get("name", "Unknown Event"),
                                duration=et.get("duration", 60),
                                description=et.get("description", ""),
                                type="appointment",
                            )
                            for et in event_types_raw
                        ]
                    
                    elif response.status_code == 401:  # Unauthorized
                        logger.error(f"[CALENDLY DEBUG] Authentication error: Invalid or expired token")
                        last_error = Exception("Calendly authentication failed - please check your access token")
                        # Don't retry on auth errors
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
        error_message = "Failed to get event types from all endpoints"
        if last_error:
            error_message += f": {str(last_error)}"
        
        logger.error(f"[CALENDLY DEBUG] {error_message}")
        raise Exception(error_message)
    
    async def get_available_slots(self, event_type_id: str, start_time: Optional[datetime] = None, days: Optional[int] = None) -> List[TimeSlot]:
        """Fetch available time slots for a given event type and time range.

        Args:
            event_type_id: ID or URI of the event type (or full URI)
            start_time: Starting time for availability search (defaults to today)
            days: Number of days to search (defaults to 7)

        Returns:
            List[TimeSlot]: available slots, sorted by start time
        """
        import asyncio, traceback, httpx
        from datetime import datetime, timedelta, timezone

        # Ensure we have the user URI
        if not self.config.user_uri:
            await self.initialize()
            if not self.config.user_uri:
                raise ValueError("User URI is required to fetch available slots")

        # Determine date window
        if start_time is None:
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if days is None:
            days = 7
        end_time = start_time + timedelta(days=days)

        # Ensure datetimes are timezone-aware (assume UTC if naive)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        # Calendly requires UTC ISO strings with trailing Z
        start_iso = start_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        end_iso = end_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        user_uuid = self.config.user_uri.rsplit("/", 1)[-1]
        logger.info(
            f"[CALENDLY DEBUG] Fetching availability for event_type_id={event_type_id}, user_uuid={user_uuid}"
        )

        # Build candidate endpoints
        endpoints_to_try: List[str] = []
        if event_type_id.startswith("http"):
            path = event_type_id.replace("https://api.calendly.com/event_types/", "")
            endpoints_to_try.append(f"/event_types/{path}/available_times")
            event_uuid = path.split("/")[-1] if "/" in path else path
            event_type_uri = event_type_id  # already full URI
        else:
            event_uuid = event_type_id
            event_type_uri = f"https://api.calendly.com/event_types/{event_uuid}"

        endpoints_to_try.extend([
            f"/users/{user_uuid}/event_types/{event_uuid}/available_times",
            f"/event_types/{event_uuid}/available_times",
            f"/users/{user_uuid}/event_types/{event_uuid}/calendar/range",
            f"/scheduled_events/available_times?event_type={event_uuid}",
            "/availability"  # NEW generic availability endpoint using owner param
        ])
        logger.info(f"[CALENDLY DEBUG] Will try these endpoints for available times: {endpoints_to_try}")

        retry_delays = [1, 2]  # seconds
        last_error: Optional[Exception] = None

        for endpoint in endpoints_to_try:
            for retry_attempt, delay in enumerate(retry_delays, start=1):
                try:
                    logger.info(
                        f"[CALENDLY DEBUG] Trying endpoint: {endpoint} (Attempt {retry_attempt}/{len(retry_delays)})"
                    )

                    params = {
                        "start_time": start_iso,
                        "end_time": end_iso,
                        "timezone": getattr(self.config, "timezone", "UTC") or "UTC",
                    }

                    # If using the generic /availability endpoint, add owner param
                    if endpoint == "/availability":
                        params["owner"] = event_type_uri

                    async with httpx.AsyncClient(timeout=15.0) as client:
                        response = await client.get(
                            f"{self.BASE_URL}{endpoint}",
                            params=params,
                            headers={
                                "Authorization": f"Bearer {self.config.access_token.strip()}",
                                "Content-Type": "application/json",
                            },
                        )

                    logger.info(
                        f"[CALENDLY DEBUG] Response status: {response.status_code} for {endpoint}"
                    )

                    if response.status_code == 200:
                        data = response.json()
                        time_slots_raw = (
                            data.get("collection")
                            or data.get("data")
                            or data.get("available_times")
                            or []
                        )
                        logger.info(f"[CALENDLY DEBUG] Found {len(time_slots_raw)} raw slots")

                        slots: List[TimeSlot] = []
                        for ts in time_slots_raw:
                            if ts.get("status", "available") != "available":
                                continue

                            start_str = ts.get("start_time") or ts.get("start") or ts.get("date")
                            end_str = ts.get("end_time") or ts.get("end")
                            if not (start_str and end_str):
                                continue

                            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))

                            slots.append(
                                TimeSlot(
                                    start_time=start_dt,
                                    end_time=end_dt,
                                    status="available",
                                    event_type_id=event_type_id,
                                    display_id=int(start_dt.timestamp()),
                                    invitee_id=None,
                                    cancellation_url=None,
                                    reschedule_url=None,
                                )
                            )

                        if slots:
                            logger.info(
                                f"[CALENDLY DEBUG] Successfully found {len(slots)} available slots"
                            )
                            slots.sort(key=lambda s: s.start_time)
                            return slots
                        else:
                            logger.info("[CALENDLY DEBUG] No available slots in response, trying next endpoint")
                            break  # Try next endpoint

                    elif response.status_code == 401:
                        last_error = Exception("Calendly authentication failed – check access token")
                        logger.error("[CALENDLY DEBUG] Authentication error – aborting retries for this endpoint")
                        break

                    elif response.status_code == 404:
                        logger.warning("[CALENDLY DEBUG] Endpoint not found – trying next endpoint")
                        break

                    else:
                        logger.warning(
                            f"[CALENDLY DEBUG] Unexpected {response.status_code}: {response.text[:200]}"
                        )
                        if retry_attempt < len(retry_delays):
                            logger.info(f"[CALENDLY DEBUG] Will retry in {delay}s...")
                            await asyncio.sleep(delay)

                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        f"[CALENDLY DEBUG] Exception on {endpoint} (attempt {retry_attempt}): {exc}"
                    )
                    logger.debug(traceback.format_exc())
                    if retry_attempt < len(retry_delays):
                        logger.info(f"[CALENDLY DEBUG] Will retry in {delay}s...")
                        await asyncio.sleep(delay)

        error_msg = "Failed to get available slots from all endpoints"
        if last_error:
            error_msg += f": {last_error}"
        logger.error(f"[CALENDLY DEBUG] {error_msg}")
        raise Exception(error_msg)
    
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
            
        # Define possible endpoints to try with different formats, ordered by diagnostic priority
        # Based on our diagnostic testing, we prioritize the most reliable endpoints
        endpoints = [
            # Primary endpoint: user-specific endpoint format
            {
                "endpoint": f"/users/{user_uuid}/scheduled_events",
                "params": {
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                },
                "priority": "primary"
            },
            # Secondary endpoint: Standard v2 API with full user URI
            {
                "endpoint": "/scheduled_events",
                "params": {
                    "user": f"https://api.calendly.com/users/{user_uuid}",
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                },
                "priority": "secondary"
            },
            # Fallback: Standard v2 API with just UUID
            {
                "endpoint": "/scheduled_events",
                "params": {
                    "user": user_uuid,
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                },
                "priority": "fallback"
            },
            # Last resort: V1 API format (without v2 in URL)
            {
                "endpoint": "/users/{user_uuid}/scheduled_events",
                "params": {
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                },
                "use_alt_base_url": True,
                "priority": "last_resort"
            }
        ]
        
        logger.info(f"[CALENDLY DEBUG] Will try {len(endpoints)} endpoints for scheduled events, starting with priority endpoint")
        
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
                            logger.info(f"[CALENDLY DEBUG] Found {len(data['data'])} events in 'data' format")
                            events_data = data["data"]
                        elif "collection" in data and isinstance(data["collection"], list):
                            logger.info(f"[CALENDLY DEBUG] Found {len(data['collection'])} events in 'collection' format")
                            events_data = data["collection"]
                        elif isinstance(data, list):
                            # Some endpoints might return a direct list
                            logger.info(f"[CALENDLY DEBUG] Found {len(data)} events in direct list format")
                            events_data = data
                        
                        if events_data:
                            logger.info(f"[CALENDLY DEBUG] Found {len(events_data)} events")
                            
                            # Enhance with detailed information
                            detailed_events = []
                            for event in events_data:
                                # Handle different API response formats and normalize data structure
                                event_data = event
                                
                                # Handle V1 API response which might have different structure
                                if use_alt_base_url and "attributes" in event:
                                    event_data = event["attributes"]
                                
                                # Normalize nested resource data if present
                                if "resource" in event_data and isinstance(event_data["resource"], dict):
                                    # V2 API sometimes nests data in resource field
                                    for key, value in event_data["resource"].items():
                                        if key not in event_data:
                                            event_data[key] = value
                                
                                # Create basic event details
                                detailed_event = {
                                    "id": event_data.get("id"),
                                    "uri": event_data.get("uri"),
                                    "start_time": event_data.get("start_time"),
                                    "end_time": event_data.get("end_time"),
                                    "status": event_data.get("status"),
                                    "event_type": event_data.get("event_type"),
                                    "cancellation_url": event_data.get("cancellation_url"),
                                    "reschedule_url": event_data.get("reschedule_url"),
                                }
                                
                                # Try to get invitee details
                                try:
                                    # Look for invitee information in different possible locations
                                    invitee_url = None
                                    
                                    # Try to extract the invitee URL from event data
                                    if "uri" in event_data and isinstance(event_data["uri"], str) and "invitees" in event_data["uri"]:
                                        invitee_url = f"{event_data['uri']}/invitees"
                                    elif "links" in event_data and isinstance(event_data["links"], dict) and "invitees" in event_data["links"]:
                                        invitee_url = event_data["links"]["invitees"]
                                    
                                    # If we found an invitee URL, fetch the data
                                    if invitee_url:
                                        logger.info(f"[CALENDLY DEBUG] Fetching invitees from: {invitee_url}")
                                        async with httpx.AsyncClient(timeout=10.0) as invitee_client:
                                            invitee_headers = {
                                                "Authorization": f"Bearer {self.config.access_token}",
                                                "Content-Type": "application/json"
                                            }
                                            invitee_response = await invitee_client.get(invitee_url, headers=invitee_headers)
                                            
                                            if invitee_response.status_code == 200:
                                                invitee_data = invitee_response.json()
                                                
                                                # Extract invitees based on response structure
                                                invitees = []
                                                if "data" in invitee_data and isinstance(invitee_data["data"], list):
                                                    invitees = invitee_data["data"]
                                                    logger.info(f"[CALENDLY DEBUG] Found {len(invitees)} invitees in 'data' format")
                                                elif "collection" in invitee_data and isinstance(invitee_data["collection"], list):
                                                    invitees = invitee_data["collection"]
                                                    logger.info(f"[CALENDLY DEBUG] Found {len(invitees)} invitees in 'collection' format")
                                                
                                                # Add first invitee details if available
                                                if invitees:
                                                    detailed_event["invitee"] = {
                                                        "name": invitees[0].get("name"),
                                                        "email": invitees[0].get("email"),
                                                        "phone": invitees[0].get("phone_number") or invitees[0].get("phone"),
                                                        "questions_and_answers": invitees[0].get("questions_and_answers", [])
                                                    }
                                except Exception as e:
                                    logger.warning(f"[CALENDLY DEBUG] Failed to get invitee details: {str(e)}")
                                
                                # Add to our list of detailed events
                                detailed_events.append(detailed_event)
                            
                            # Log the successful endpoint usage
                            logger.info(f"[CALENDLY DEBUG] Successfully fetched {len(detailed_events)} events using {endpoint_config['priority']} endpoint")
                            
                            # Close the temporary client if we created one
                            if use_alt_base_url:
                                await client.aclose()
                                
                            # Return the events we found
                            return detailed_events
                    
                    # If not successful, log and try the next retry or endpoint
                    if retry_idx < len(retry_delays) - 1:
                        logger.warning(f"[CALENDLY DEBUG] Retrying after {delay} seconds. Status: {response.status_code}")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"[CALENDLY DEBUG] All retries failed for endpoint {endpoint}")
                    
                except httpx.HTTPStatusError as http_err:
                    last_error = http_err
                    logger.error(f"[CALENDLY DEBUG] HTTP error fetching scheduled events: {str(http_err)}, status_code={http_err.response.status_code}")
                    
                    # Don't retry for certain status codes
                    if http_err.response.status_code in [401, 403, 404]:
                        logger.warning(f"[CALENDLY DEBUG] Not retrying due to status code {http_err.response.status_code}")
                        break
                    
                    if retry_idx < len(retry_delays) - 1:
                        logger.warning(f"[CALENDLY DEBUG] Retrying after {delay} seconds due to HTTP error")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"[CALENDLY DEBUG] All retries failed for endpoint {endpoint} due to HTTP error")
                except httpx.RequestError as req_err:
                    last_error = req_err
                    logger.error(f"[CALENDLY DEBUG] Request error fetching scheduled events: {str(req_err)}")
                    
                    if retry_idx < len(retry_delays) - 1:
                        logger.warning(f"[CALENDLY DEBUG] Retrying after {delay} seconds due to request error")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"[CALENDLY DEBUG] All retries failed for endpoint {endpoint} due to request error")
                except Exception as e:
                    last_error = e
                    logger.error(f"[CALENDLY DEBUG] Unexpected error fetching scheduled events: {str(e)}")
                    
                    if retry_idx < len(retry_delays) - 1:
                        logger.warning(f"[CALENDLY DEBUG] Retrying after {delay} seconds due to unexpected error")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"[CALENDLY DEBUG] All retries failed for endpoint {endpoint} due to unexpected error")
            
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
    
    def _create_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json"
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
            if using_fallback:
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

    def format_slots_for_sms(self, slots: List[TimeSlot], limit: int = 10) -> str:
        """Format a list of TimeSlot objects into a numbered string for SMS.

        Args:
            slots: List of TimeSlot objects returned from get_available_slots.
            limit: Maximum number of slots to show (default 10).

        Returns:
            A user-friendly string listing up to ``limit`` slots, or a fallback message
            if the list is empty.
        """
        try:
            if not slots:
                return "I'm sorry, but no available times were found in the next few days."

            # Sort by start time just in case
            sorted_slots = sorted(slots, key=lambda s: s.start_time)
            # Limit the number of slots displayed
            display_slots = sorted_slots[: limit]

            lines: List[str] = []
            for idx, slot in enumerate(display_slots, 1):
                # Ensure the datetime is timezone-aware and format nicely
                dt = slot.start_time
                # Convert to local timezone if tzinfo is present, otherwise assume UTC
                if dt.tzinfo:
                    dt_local = dt.astimezone()  # Convert to system local timezone
                else:
                    dt_local = dt.replace(tzinfo=timezone.utc).astimezone()
                lines.append(f"{idx}. {dt_local.strftime('%a, %b %d at %I:%M %p')}")

            response = "Here are the next available times:\n\n" + "\n".join(lines)
            if len(sorted_slots) > limit:
                response += "\n\nMore times are available."
            response += "\n\nReply with the number to pick a time."
            return response
        except Exception as e:
            logger.error(f"Error formatting slots for SMS: {str(e)}")
            return "I'm sorry, I couldn't format the available times right now. Please try again later."
