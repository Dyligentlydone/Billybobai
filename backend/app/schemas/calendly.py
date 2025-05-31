from pydantic import BaseModel, HttpUrl, Field
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

class SMSNotificationSettings(BaseModel):
    """Settings for Calendly's native SMS notifications"""
    enabled: bool = True
    include_cancel_link: bool = True
    include_reschedule_link: bool = True
    confirmation_message: str = "Your appointment has been confirmed."
    reminder_message: str = "Reminder: You have an upcoming appointment."
    cancellation_message: str = "Your appointment has been cancelled."
    reschedule_message: str = "Your appointment has been rescheduled."

class CalendlyConfig(BaseModel):
    enabled: bool = False
    access_token: str
    user_uri: Optional[str] = None  # Now optional as system will fetch it
    organization_uri: Optional[str] = None  # Organization URI for admin access
    webhook_uri: Optional[str] = None
    default_event_type: str = ""
    event_types: Dict[str, CalendlyEventType] = {}
    reminder_hours: List[int] = [24, 1]  # Send reminders 24h and 1h before
    allow_cancellation: bool = True
    allow_rescheduling: bool = True
    booking_window_days: int = 14  # How many days in advance can book
    min_notice_hours: int = 1  # Minimum hours notice needed for booking
    sms_notifications: SMSNotificationSettings = Field(default_factory=SMSNotificationSettings)

class TimeSlot(BaseModel):
    """A time slot for a Calendly event"""
    start_time: datetime
    end_time: datetime
    event_type_id: str
    display_id: int

class BookingRequest(BaseModel):
    """Request schema for creating a Calendly booking"""
    event_type_id: str
    start_time: datetime
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

class Booking(BaseModel):
    """A Calendly booking"""
    id: str
    event_type: CalendlyEventType
    start_time: datetime
    end_time: datetime
    customer_name: str
    customer_phone: Optional[str] = None
    status: str
    cancellation_url: Optional[str] = None
    reschedule_url: Optional[str] = None

class WebhookEvent(BaseModel):
    """A Calendly webhook event"""
    event: str
    payload: Dict[str, Any]

class SMSBookingState(BaseModel):
    """State for SMS-based booking flow"""
    phone: str
    step: str
    event_type_id: Optional[str] = None
    selected_slot: Optional[int] = None
    available_slots: List[TimeSlot] = []
    booking: Optional[Booking] = None
    last_update: datetime = Field(default_factory=datetime.now)

class CalendlyTokenRequest(BaseModel):
    """Request schema for validating a Calendly token"""
    access_token: str

# Forward reference for type hints
WorkflowStepType = Any  # Will be used as a type annotation for WorkflowStep

class WorkflowCreate(BaseModel):
    """Create a Calendly Workflow for SMS notifications"""
    name: str
    owner_uri: str
    steps: List[Any]  # Using Any instead of forward reference to avoid circular imports

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
