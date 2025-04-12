from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
import hmac
import hashlib
import base64
import json
import os
from ..services.twilio_service import TwilioService
from ..services.sendgrid_service import SendGridService
from ..services.zendesk_service import ZendeskService
from ..services.ai_service import AIService
from functools import wraps

webhooks = Blueprint('webhooks', __name__)

# Initialize services - they'll be None if credentials aren't available
twilio_service = None
sendgrid_service = None
zendesk_service = None
ai_service = None

try:
    twilio_service = TwilioService()
    sendgrid_service = SendGridService()
    zendesk_service = ZendeskService()
    ai_service = AIService()
except Exception as e:
    print(f"Warning: Some services failed to initialize: {str(e)}")

def verify_twilio_signature(f):
    """Decorator to verify Twilio webhook signatures."""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        twilio_signature = request.headers.get('X-Twilio-Signature', '')
        url = request.url
        params = request.form.to_dict()
        
        # Validate request is from Twilio
        if not twilio_service.validate_webhook({"signature": twilio_signature, "url": url, "params": params}):
            return jsonify({"error": "Invalid signature"}), 403
        return await f(*args, **kwargs)
    return decorated_function

def verify_sendgrid_signature(f):
    """Decorator to verify SendGrid webhook signatures."""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Twilio-Email-Event-Webhook-Signature', '')
        timestamp = request.headers.get('X-Twilio-Email-Event-Webhook-Timestamp', '')
        
        if not signature or not timestamp:
            return jsonify({"error": "Missing signature headers"}), 401
            
        # Verify signature
        payload = timestamp + request.get_data().decode('utf-8')
        hmac_obj = hmac.new(
            key=os.getenv('SENDGRID_WEBHOOK_VERIFY_KEY').encode(),
            msg=payload.encode(),
            digestmod=hashlib.sha256
        )
        calculated_sig = hmac_obj.hexdigest()

        if not hmac.compare_digest(calculated_sig, signature):
            return jsonify({"error": "Invalid signature"}), 401

        return await f(*args, **kwargs)
    return decorated_function

def verify_zendesk_signature(f):
    """Decorator to verify Zendesk webhook signatures."""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Zendesk-Webhook-Signature', '')
        if not signature:
            return jsonify({"error": "Missing signature header"}), 401
            
        # Validate request is from Zendesk
        if not zendesk_service.validate_webhook({"signature": signature}):
            return jsonify({"error": "Invalid signature"}), 403
        return await f(*args, **kwargs)
    return decorated_function

@webhooks.route('/twilio/webhook', methods=['POST'])
@verify_twilio_signature
async def twilio_webhook():
    """Handle incoming Twilio webhooks (SMS, Voice, WhatsApp)."""
    try:
        # Get message details
        message_type = request.form.get('MessageType', 'sms')
        from_number = request.form.get('From')
        body = request.form.get('Body', '')
        
        if message_type == 'voice':
            # Handle voice calls
            response = VoiceResponse()
            response.say('Thank you for calling. Please leave a message after the beep.')
            response.record(max_length=30)
            response.hangup()
            return str(response)
        
        # For SMS/WhatsApp, check if AI is enabled for this number
        if body:
            # Generate AI response if configured
            workflow_response = await ai_service.analyze_requirements(body)
            response_text = "Thank you for your message. "
            
            if workflow_response.twilio:
                response_text += "I'll help you with that right away."
            else:
                response_text += "A representative will get back to you soon."

            # Create Twilio response
            response = MessagingResponse()
            response.message(response_text)
            
            # Create Zendesk ticket if needed
            if workflow_response.zendesk:
                await zendesk_service.create_ticket(
                    subject=f"New message from {from_number}",
                    description=body,
                    requester_email=from_number + "@sms.customer.com"  # Virtual email for SMS users
                )
            
            return str(response)
        
        return '', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@webhooks.route('/sendgrid/webhook', methods=['POST'])
@verify_sendgrid_signature
async def sendgrid_webhook():
    """Handle SendGrid email events (delivered, opened, clicked, etc.)."""
    try:
        events = request.get_json()
        
        for event in events:
            event_type = event.get('event')
            email = event.get('email')
            timestamp = event.get('timestamp')
            
            # Handle different event types
            if event_type == 'bounce':
                # Create Zendesk ticket for bounced emails
                await zendesk_service.create_ticket(
                    subject=f"Email bounce for {email}",
                    description=f"Email bounced at {timestamp}. Reason: {event.get('reason')}",
                    priority="high"
                )
            elif event_type == 'spamreport':
                # Create Zendesk ticket for spam reports
                await zendesk_service.create_ticket(
                    subject=f"Spam report from {email}",
                    description=f"Spam report received at {timestamp}",
                    priority="urgent"
                )
            
            # Log the event (you would typically store this in your database)
            print(f"SendGrid event: {event_type} for {email}")
        
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@webhooks.route('/zendesk/webhook', methods=['POST'])
@verify_zendesk_signature
async def zendesk_webhook():
    """Handle Zendesk ticket events (created, updated, solved, etc.)."""
    try:
        event = request.get_json()
        
        ticket = event.get('ticket', {})
        ticket_id = ticket.get('id')
        status = ticket.get('status')
        priority = ticket.get('priority')
        
        if status == 'solved':
            # Send thank you email via SendGrid
            requester_email = ticket.get('requester', {}).get('email')
            if requester_email:
                await sendgrid_service.send_email({
                    "to": requester_email,
                    "template_id": os.getenv('SENDGRID_THANK_YOU_TEMPLATE_ID'),
                    "template_data": {
                        "ticket_id": ticket_id,
                        "satisfaction_survey_url": f"https://survey.example.com/{ticket_id}"
                    }
                })
        
        elif priority == 'urgent':
            # Send SMS notification for urgent tickets
            assignee = ticket.get('assignee', {})
            if assignee.get('phone'):
                await twilio_service.send_message({
                    "to": assignee['phone'],
                    "message": f"Urgent ticket #{ticket_id} requires immediate attention"
                })
        
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
