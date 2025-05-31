import httpx
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
                
        try:
            logger.info(f"Fetching event types for user UUID: {user_uuid}")
            response = await self.client.get(
                f"/users/{user_uuid}/event_types"
            )
            response.raise_for_status()
            return [
                CalendlyEventType(**event_type)
                for event_type in response.json()["data"]
            ]
        except Exception as e:
            logger.error(f"Failed to get event types: {str(e)}")
            raise
    
    async def get_available_slots(
        self,
        event_type_id: str,
        start_time: Optional[datetime] = None,
        days: Optional[int] = None
    ) -> List[TimeSlot]:
        """Get available time slots for an event type"""
        logger.info(f"Fetching available slots for event_type_id: {event_type_id}")
        
        if not start_time:
            start_time = datetime.now()
        
        if not days:
            days = self.config.booking_window_days or 14
            
        end_time = start_time + timedelta(days=days)
        
        # Format dates for Calendly API
        start_time_iso = start_time.isoformat()
        end_time_iso = end_time.isoformat()
        
        logger.info(f"Searching for slots between {start_time_iso} and {end_time_iso}")
        
        params = {
            "start_time": start_time_iso,
            "end_time": end_time_iso
        }
        
        try:
            # Convert event_type_id to a proper Calendly URI if it's not already
            full_event_type_uri = None
            
            # If it's already a full URI, use it directly
            if event_type_id.startswith('http'):
                full_event_type_uri = event_type_id
                logger.info(f"Using provided full event type URI: {full_event_type_uri}")
            else:
                # Extract user UUID to construct the event type URI
                user_uuid = None
                if self.config.user_uri:
                    if '/' in self.config.user_uri:
                        user_uuid = self.config.user_uri.split('/')[-1]
                    else:
                        user_uuid = self.config.user_uri
                
                if not user_uuid:
                    raise ValueError("User UUID is required to construct event type URI")
                
                # Handle different formats of event_type_id
                if '/' in event_type_id:
                    # Assume it's a partial URI like 'user_uuid/event_type_slug'
                    full_event_type_uri = f"https://api.calendly.com/event_types/{event_type_id}"
                else:
                    # Assume it's just a slug like 'consultation-demo'
                    full_event_type_uri = f"https://api.calendly.com/event_types/{user_uuid}/{event_type_id}"
                
                logger.info(f"Constructed event type URI: {full_event_type_uri}")
            
            # Extract just the UUID or path part for the API endpoint
            if full_event_type_uri.startswith('https://api.calendly.com/event_types/'):
                endpoint_path = full_event_type_uri.replace('https://api.calendly.com/event_types/', '')
                logger.info(f"Making API request to: /event_types/{endpoint_path}/available_times")
                response = await self.client.get(f"/event_types/{endpoint_path}/available_times", params=params)
            else:
                # Fallback to using the original ID directly
                logger.info(f"Making API request to: /event_types/{event_type_id}/available_times")
                response = await self.client.get(f"/event_types/{event_type_id}/available_times", params=params)
            
            # Log response status
            logger.info(f"Calendly API response status: {response.status_code}")
            
            # For debugging, log part of the response content
            response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
            logger.info(f"Response preview: {response_text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # Log the number of available slots found
            slots_count = len(data.get("data", []))
            logger.info(f"Found {slots_count} available slots")
            
            slots = []
            
            for slot_data in data.get("data", []):
                start_time = datetime.fromisoformat(slot_data["start_time"].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(slot_data["end_time"].replace("Z", "+00:00"))
                
                # Convert to naive datetime for easier comparison
                start_time = start_time.replace(tzinfo=None)
                end_time = end_time.replace(tzinfo=None)
                
                slots.append(TimeSlot(
                    start_time=start_time,
                    end_time=end_time,
                    display_id=slot_data.get("display_id", "")
                ))
            
            # Log a few sample slots for debugging
            if slots:
                sample_slots = slots[:2]
                logger.info(f"Sample slots: {[s.start_time.isoformat() for s in sample_slots]}")
            
            return slots
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while getting available slots: {e.response.status_code} - {str(e)}")
            try:
                error_body = e.response.json()
                logger.error(f"Error details: {error_body}")
            except:
                logger.error(f"Could not parse error response body")
            raise
        except Exception as e:
            logger.error(f"Failed to get available slots: {str(e)}")
            raise
    
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
        
        try:
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
                
            logger.info(f"Fetching scheduled events using user UUID: {user_uuid}")
                
            # Use the fully qualified URI for user - Calendly API requires full URIs
            user_uri = f"https://api.calendly.com/users/{user_uuid}"
            logger.info(f"Using user URI for API request: {user_uri}")
                
            # Use the correct endpoint structure for the API call
            response = await self.client.get(
                "/scheduled_events",
                params={
                    "user": user_uri,  # Use the full URI, not just the UUID
                    "min_start_time": min_start_time,
                    "max_start_time": max_start_time,
                    "status": "active"
                }
            )
            
            response.raise_for_status()
            events_data = response.json().get("data", [])
            
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
                
                # Try to get invitee details
                try:
                    if "uri" in event:
                        invitee_response = await self.client.get(f"{event['uri']}/invitees")
                        if invitee_response.status_code == 200:
                            invitees = invitee_response.json().get("data", [])
                            if invitees:
                                detailed_event["invitee"] = {
                                    "name": invitees[0].get("name"),
                                    "email": invitees[0].get("email"),
                                    "phone": invitees[0].get("phone_number")
                                }
                except Exception as e:
                    logger.warning(f"Failed to get invitee details: {str(e)}")
                    
                detailed_events.append(detailed_event)
                
            return detailed_events
        except Exception as e:
            logger.error(f"Failed to get scheduled events: {str(e)}")
            raise
    
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
        
        # Get all events for the day
        events = await self.get_scheduled_events(day_start, day_end)
        
        # Look for exact match (within 15 minutes)
        exact_match = None
        closest_time = None
        closest_diff = timedelta(days=1)  # Initialize with a large value
        
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
            logger.warning(f"Failed to get available slots: {str(e)}")
        
        # Prepare result
        result = {
            "exists": exact_match is not None,
            "details": exact_match if exact_match else None,
            "closest_time": closest_time.isoformat() if closest_time else None,
            "closest_event": closest_event if 'closest_event' in locals() else None,
            "available_slots": available_slots,
            "search_date": search_date.isoformat()
        }
        
        return result
    
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
            
            # Get event types to find the default one
            event_types = await self.get_event_types()
            if not event_types:
                logger.error("No event types found for this Calendly account")
                return {
                    "success": False,
                    "error": "No event types found",
                    "message": "No event types are configured in your Calendly account",
                    "available_days": []
                }
                
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
                
            if not default_event_type:
                logger.error("Could not find a valid event type")
                return {
                    "success": False,
                    "error": "Event type not found",
                    "message": "Could not find a valid event type in your Calendly account",
                    "available_days": []
                }
                
            logger.info(f"Using event type: {default_event_type.name} (ID: {default_event_type.id})")
                
            # Get all available slots for this period
            slots = await self.get_available_slots(
                event_type_id=default_event_type.id,
                start_time=start_date,
                days=days
            )
            
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
                "available_days": available_days
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
