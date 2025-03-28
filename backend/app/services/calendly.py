import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from ..schemas.calendly import (
    CalendlyConfig,
    TimeSlot,
    BookingRequest,
    Booking,
    CalendlyEventType,
    WebhookEvent,
    SMSBookingState
)

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
            cancellation_url=booking_data.get("cancellation_url"),
            reschedule_url=booking_data.get("reschedule_url")
        )
    
    async def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking"""
        response = await self.client.post(
            f"/bookings/{booking_id}/cancel"
        )
        return response.status_code == 200
    
    def format_slots_for_sms(self, slots: List[TimeSlot]) -> str:
        """Format time slots for SMS display"""
        if not slots:
            return "No available slots in the next few days. Please try a different date range."
            
        slot_texts = []
        for slot in slots[:5]:  # Show max 5 slots
            slot_texts.append(
                f"{slot.display_id}. {slot.start_time.strftime('%a %b %d at %I:%M %p')}"
            )
            
        return self.config.sms_templates["available_slots"].format(
            slots="\n".join(slot_texts)
        )

    def get_booking_state(self, phone_number: str) -> Optional[SMSBookingState]:
        """Get the current booking state for a phone number"""
        state = self._sms_states.get(phone_number)
        if state and state.expires_at > datetime.now():
            return state
        return None

    def set_booking_state(self, phone_number: str, state: SMSBookingState):
        """Set the booking state for a phone number"""
        self._sms_states[phone_number] = state

    def clear_booking_state(self, phone_number: str):
        """Clear the booking state for a phone number"""
        if phone_number in self._sms_states:
            del self._sms_states[phone_number]

    def format_booking_confirmation(self, booking: Booking) -> str:
        """Format booking confirmation message for SMS"""
        date = booking.start_time.strftime("%A, %B %d")
        time = booking.start_time.strftime("%I:%M %p")
        cancellation_info = ""
        
        if self.config.allow_cancellation:
            cancellation_info = f"\nTo cancel, visit: {booking.cancellation_url}"
        
        return self.config.sms_templates["booking_confirmation"].format(
            date=date,
            time=time,
            cancellation_info=cancellation_info
        )

    def format_reminder(self, booking: Booking) -> str:
        """Format reminder message for SMS"""
        return self.config.sms_templates["reminder"].format(
            date=booking.start_time.strftime("%A, %B %d"),
            time=booking.start_time.strftime("%I:%M %p")
        )

    async def process_webhook_event(self, event: WebhookEvent) -> Optional[Tuple[str, str]]:
        """Process a webhook event and return (phone_number, message) if SMS should be sent"""
        booking_data = event.payload.get("booking", {})
        phone = booking_data.get("customer", {}).get("phone")
        
        if not phone:
            return None
            
        if event.event == "invitee.canceled":
            message = self.config.sms_templates["cancellation"].format(
                date=datetime.fromisoformat(booking_data["start_time"]).strftime("%A, %B %d"),
                time=datetime.fromisoformat(booking_data["start_time"]).strftime("%I:%M %p")
            )
            return (phone, message)
            
        elif event.event == "invitee.rescheduled":
            message = self.config.sms_templates["reschedule"].format(
                date=datetime.fromisoformat(booking_data["start_time"]).strftime("%A, %B %d"),
                time=datetime.fromisoformat(booking_data["start_time"]).strftime("%I:%M %p")
            )
            return (phone, message)
            
        return None
