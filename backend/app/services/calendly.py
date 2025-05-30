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
    WorkflowCreate,
    WorkflowStep
)
import logging

logger = logging.getLogger(__name__)

class CalendlyService:
    BASE_URL = "https://api.calendly.com/v2"
    
    def __init__(self, config: CalendlyConfig):
        self.config = config
        
        # Make sure token is stripped of any whitespace
        if hasattr(config, 'access_token') and config.access_token:
            config.access_token = config.access_token.strip()
            
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

        # Create steps for the workflow
        steps: List[WorkflowStep] = []
        
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
        if not start_time:
            start_time = datetime.now() + timedelta(hours=self.config.min_notice_hours)
        if not days:
            days = self.config.booking_window_days
            
        end_time = start_time + timedelta(days=days)
        
        response = await self.client.get(
            f"/event_types/{event_type_id}/available_times",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )
        response.raise_for_status()
        
        slots = []
        for i, slot_data in enumerate(response.json()["data"], 1):
            slot = TimeSlot(
                start_time=datetime.fromisoformat(slot_data["start_time"]),
                end_time=datetime.fromisoformat(slot_data["end_time"]),
                event_type_id=event_type_id,
                display_id=i
            )
            slots.append(slot)
        return slots
    
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
