from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Literal, Any
from datetime import datetime

class CalendlyEventType(BaseModel):
    id: str
    name: str
    duration: int
    description: Optional[str] = None
    price: Optional[float] = None
    type: str = "appointment"
    color: Optional[str] = None

class CalendlyConfig(BaseModel):
    enabled: bool = False
    access_token: str
    user_uri: Optional[str] = None  # Now optional as system will fetch it
    webhook_uri: Optional[str] = None
    default_event_type: str
    event_types: Dict[str, CalendlyEventType] = {}
    reminder_hours: List[int] = [24, 1]  # Send reminders 24h and 1h before
    allow_cancellation: bool = True
    allow_rescheduling: bool = True
    booking_window_days: int = 14  # How many days in advance can book
    min_notice_hours: int = 1  # Minimum hours notice needed for booking
    sms_notifications: SMSNotificationSettings = SMSNotificationSettings()

class SMSNotificationSettings(BaseModel):
    """Settings for Calendly's native SMS notifications"""
    enabled: bool = True
    include_cancel_link: bool = True
    include_reschedule_link: bool = True
    confirmation_message: str
    reminder_message: str
    cancellation_message: str
    reschedule_message: str

class WorkflowCreate(BaseModel):
    """Create a Calendly Workflow for SMS notifications"""
    name: str
    owner_uri: str
    steps: List[WorkflowStep]

class WorkflowStep(BaseModel):
    """A step in a Calendly Workflow"""
    action: Literal["send_sms"] = "send_sms"
    trigger: Literal[
        "invitee.created", 
        "invitee.canceled", 
        "invitee.rescheduled",
        "before_event"
    ]
    before_event_minutes: Optional[int] = None  # Only for "before_event" trigger
    message_template: str

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    event_type_id: str
    available: bool = True
    display_id: Optional[int] = None  # For SMS slot selection

class BookingRequest(BaseModel):
    event_type_id: str
    start_time: datetime
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: str
    notes: Optional[str] = None

class Booking(BaseModel):
    id: str
    event_type: CalendlyEventType
    start_time: datetime
    end_time: datetime
    customer_name: str
    customer_phone: str
    status: Literal["active", "cancelled", "rescheduled"]
    cancellation_url: Optional[str] = None
    reschedule_url: Optional[str] = None

class WebhookEvent(BaseModel):
    event: Literal["invitee.created", "invitee.canceled", "invitee.rescheduled"]
    payload: Dict
    created_at: datetime

class SMSBookingState(BaseModel):
    """Tracks the state of a booking conversation via SMS"""
    phone_number: str
    state: Literal["selecting_event_type", "viewing_slots", "confirming_booking", "completed"]
    selected_event_type: Optional[str] = None
    available_slots: List[TimeSlot] = []
    selected_slot: Optional[TimeSlot] = None
    last_interaction: datetime
    expires_at: datetime  # State expires after certain time for cleanup
