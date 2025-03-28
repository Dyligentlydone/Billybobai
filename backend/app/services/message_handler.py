from typing import Optional, Dict, Any
from datetime import datetime
from .calendly import CalendlyService
from ..schemas.calendly import BookingRequest, CalendlyConfig
import re

class MessageHandler:
    def __init__(self, business_config: Dict[str, Any]):
        self.config = business_config
        if business_config.get('calendly', {}).get('enabled'):
            self.calendly = CalendlyService(CalendlyConfig(**business_config['calendly']))
        else:
            self.calendly = None
        
    async def handle_message(self, message: str, context: Dict[str, Any]) -> str:
        """Handle incoming message and return appropriate response"""
        
        # Check if we're in an active booking flow
        if context.get('booking_flow'):
            return await self._handle_booking_flow(message, context)
            
        # Check if message is asking about appointments
        if self._is_appointment_request(message):
            return await self._start_booking_flow(context)
            
        # Handle other message types...
        return await self._generate_ai_response(message, context)
    
    def _is_appointment_request(self, message: str) -> bool:
        """Check if message is requesting an appointment"""
        appointment_keywords = [
            'book',
            'schedule',
            'appointment',
            'meet',
            'consultation',
            'slot',
            'time',
            'available'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in appointment_keywords)
    
    async def _start_booking_flow(self, context: Dict[str, Any]) -> str:
        """Start the appointment booking flow"""
        if not self.calendly:
            return "I apologize, but online booking is not available at the moment. Please call us to schedule an appointment."
            
        # Get available event types
        event_types = self.calendly.config.event_types
        
        if not event_types:
            return "I apologize, but there are no appointment types configured. Please contact us directly to schedule."
            
        # Format event types for selection
        options = []
        for i, (_, event_type) in enumerate(event_types.items(), 1):
            price_text = f" (${event_type.price})" if event_type.price else ""
            duration_text = f"{event_type.duration} minutes"
            options.append(f"{i}. {event_type.name} - {duration_text}{price_text}")
        
        # Update context
        context['booking_flow'] = {
            'state': 'selecting_type',
            'event_types': list(event_types.values())
        }
        
        return "What type of appointment would you like to book?\n\n" + "\n".join(options) + "\n\nReply with the number to see available times."
    
    async def _handle_booking_flow(self, message: str, context: Dict[str, Any]) -> str:
        """Handle messages within the booking flow"""
        flow = context['booking_flow']
        
        if flow['state'] == 'selecting_type':
            try:
                selection = int(message.strip()) - 1
                event_type = flow['event_types'][selection]
                
                # Get available slots
                slots = await self.calendly.get_available_slots(event_type.id)
                if not slots:
                    return "I'm sorry, but there are no available slots in the next few days. Would you like to try a different appointment type?"
                
                # Update context
                flow['state'] = 'selecting_slot'
                flow['event_type'] = event_type
                flow['slots'] = slots
                
                # Format slots for display
                return self.calendly.format_slots_for_sms(slots)
                
            except (ValueError, IndexError):
                return "Please reply with a valid number from the list above."
                
        elif flow['state'] == 'selecting_slot':
            try:
                selection = int(message.strip()) - 1
                slot = flow['slots'][selection]
                
                # Create booking
                booking = await self.calendly.create_booking(
                    BookingRequest(
                        event_type_id=flow['event_type'].id,
                        start_time=slot.start_time,
                        customer_name=context.get('customer_name', 'SMS Customer'),
                        customer_phone=context['from_number']
                    )
                )
                
                # Clear booking flow
                context['booking_flow'] = None
                
                # Format confirmation message
                msg = [
                    f"Great! Your {booking.event_type.name} is confirmed for {booking.start_time.strftime('%A, %B %d at %I:%M %p')}."
                ]
                
                if self.calendly.config.allow_cancellation and booking.cancellation_url:
                    msg.append(f"\nTo cancel: {booking.cancellation_url}")
                    
                if self.calendly.config.allow_rescheduling and booking.reschedule_url:
                    msg.append(f"\nTo reschedule: {booking.reschedule_url}")
                    
                msg.append("\nReply HELP if you need anything else!")
                
                return "\n".join(msg)
                
            except (ValueError, IndexError):
                return "Please reply with a valid number from the list above."
                
        return "I'm sorry, something went wrong. Please try booking again."
    
    async def _generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate AI response for non-booking messages"""
        # Your existing AI response generation code here
        pass
