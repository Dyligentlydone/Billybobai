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
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Content-Type": "application/json"
            }
        )
        self._sms_states: Dict[str, SMSBookingState] = {}
    
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
        # Ensure SMS workflow is set up
        if self.config.sms_notifications.enabled:
            await self.setup_sms_workflow()
            
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
