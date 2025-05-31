import httpx
from datetime import datetime, timedelta
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
                "Authorization": f"Bearer {config.access_token}",
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
                
        response = await self.client.get(
            f"/users/{self.config.user_uri}/event_types"
        )
        response.raise_for_status()
        return [
            CalendlyEventType(**event_type)
            for event_type in response.json()["data"]
        ]
    
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
            # Format the user URI properly for the API
            formatted_uri = self.format_user_uri(self.config.user_uri)
            logger.info(f"Fetching scheduled events for user {formatted_uri} from {min_start_time} to {max_start_time}")
            
            try:
                # First approach - use the formatted URI
                response = await self.client.get(
                    "/scheduled_events",
                    params={
                        "user": formatted_uri,
                        "min_start_time": min_start_time,
                        "max_start_time": max_start_time,
                        "status": "active"
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to get events with formatted URI: {str(e)}")
                # Second approach - try using just the UUID portion
                if self.config.user_uri and '/' in self.config.user_uri:
                    # Extract UUID from the URI
                    user_id = self.config.user_uri.split('/')[-1]
                    logger.info(f"Trying with extracted user ID: {user_id}")
                    response = await self.client.get(
                        "/scheduled_events",
                        params={
                            "user": user_id,
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
