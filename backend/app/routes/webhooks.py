from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
import hmac
import hashlib
import base64
import json
import os
import logging
from ..services.twilio_service import TwilioService
from ..services.sendgrid_service import SendGridService
from ..services.zendesk_service import ZendeskService
from ..services.ai_service import AIService
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

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
    def decorated_function(*args, **kwargs):
        twilio_signature = request.headers.get('X-Twilio-Signature', '')
        url = request.url
        params = request.form.to_dict()
        
        # Validate request is from Twilio
        if not twilio_service.validate_webhook({"signature": twilio_signature, "url": url, "params": params}):
            return jsonify({"error": "Invalid signature"}), 403
        return f(*args, **kwargs)
    return decorated_function

def verify_sendgrid_signature(f):
    """Decorator to verify SendGrid webhook signatures."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
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

        return f(*args, **kwargs)
    return decorated_function

def verify_zendesk_signature(f):
    """Decorator to verify Zendesk webhook signatures."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Zendesk-Webhook-Signature', '')
        if not signature:
            return jsonify({"error": "Missing signature header"}), 401
            
        # Validate request is from Zendesk
        if not zendesk_service.validate_webhook({"signature": signature}):
            return jsonify({"error": "Invalid signature"}), 403
        return f(*args, **kwargs)
    return decorated_function

@webhooks.route('/twilio/webhook', methods=['POST'])
@verify_twilio_signature
def twilio_webhook():
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
            workflow_response = ai_service.analyze_requirements(body)
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
                zendesk_service.create_ticket(
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
def sendgrid_webhook():
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
                zendesk_service.create_ticket(
                    subject=f"Email bounce for {email}",
                    description=f"Email bounced at {timestamp}. Reason: {event.get('reason')}",
                    priority="high"
                )
            elif event_type == 'spamreport':
                # Create Zendesk ticket for spam reports
                zendesk_service.create_ticket(
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
def zendesk_webhook():
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
                sendgrid_service.send_email({
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
                twilio_service.send_message({
                    "to": assignee['phone'],
                    "message": f"Urgent ticket #{ticket_id} requires immediate attention"
                })
        
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@webhooks.route('/sms/webhook/<business_id>', methods=['POST', 'GET'])
def business_specific_webhook(business_id):
    """Handle incoming Twilio webhooks for a specific business."""
    try:
        # Log that the endpoint was reached
        logger.info(f"##########################################")
        logger.info(f"SMS WEBHOOK ENDPOINT REACHED - Method: {request.method}")
        logger.info(f"REQUEST URL: {request.url}")
        logger.info(f"BUSINESS ID: {business_id}")
        logger.info(f"HEADERS: {dict(request.headers)}")
        
        if request.method == 'POST':
            logger.info(f"FORM DATA: {dict(request.form)}")
        else:
            logger.info(f"QUERY PARAMS: {dict(request.args)}")
        
        # Get message details from Twilio request
        from_number = request.form.get('From', 'unknown') if request.method == 'POST' else request.args.get('From', 'unknown')
        body = request.form.get('Body', '') if request.method == 'POST' else request.args.get('Body', '')
        
        logger.info(f"FROM: {from_number}")
        logger.info(f"BODY: {body}")
        
        # Always create a TwiML response - this is critical for Twilio
        resp = MessagingResponse()
        
        try:
            # Import models here to avoid circular import
            from ..models import Business, Workflow
            from .. import db
            
            logger.info("Attempting database query for business and workflow")
            
            # Check if business exists
            business = db.session.query(Business).filter_by(id=business_id).first()
            
            if not business:
                logger.error(f"Business not found with ID: {business_id}")
                # Always return a valid TwiML response even when business not found
                resp.message(f"Thank you for your message. We'll get back to you soon. (Business ID: {business_id} not found)")
                return str(resp)
            
            logger.info(f"Found business: {business.name if hasattr(business, 'name') else business.id}")
            
            # Get active workflow for this business
            workflow = db.session.query(Workflow).filter_by(
                business_id=business_id,
                status='ACTIVE'
            ).first()
            
            if not workflow:
                logger.error(f"NO ACTIVE WORKFLOW FOUND FOR BUSINESS ID: {business_id}")
                # Always return a valid TwiML response even when workflow not found
                resp.message("Thank you for your message. A representative will get back to you soon. (No active workflow)")
                return str(resp)
            
            # Process the message using the AI service
            if body:
                global ai_service
                # Initialize AI service if needed
                if ai_service is None:
                    from ..services.ai_service import AIService
                    ai_service = AIService()
                    logger.info("AI service initialized for SMS processing")
                
                try:
                    # Generate AI response based on workflow configuration
                    logger.info("CALLING AI SERVICE TO GENERATE RESPONSE...")
                    workflow_response = ai_service.analyze_requirements(body, workflow.actions)
                    logger.info(f"AI SERVICE RESPONSE: {workflow_response}")
                    
                    # Get response text from AI or fallback message
                    response_text = (workflow_response.get('message') or 
                                   workflow.actions.get('twilio', {}).get('fallbackMessage') or
                                   workflow.actions.get('response', {}).get('fallbackMessage') or
                                   "Thank you for your message. We'll respond shortly.")
                    
                    # Add the response to the TwiML
                    resp.message(response_text)
                    logger.info(f"SUCCESSFULLY PROCESSED MESSAGE FOR BUSINESS ID: {business_id}")
                    
                except Exception as ai_error:
                    logger.error(f"AI SERVICE ERROR: {str(ai_error)}")
                    import traceback
                    logger.error(f"AI SERVICE TRACEBACK: {traceback.format_exc()}")
                    
                    # Use fallback message from workflow if available
                    fallback_message = (workflow.actions.get('twilio', {}).get('fallbackMessage') or
                                      workflow.actions.get('response', {}).get('fallbackMessage') or
                                      "Thank you for your message. A representative will get back to you soon.")
                    
                    resp.message(fallback_message)
            else:
                # For empty message body
                resp.message("We've received your message. How can we help you today?")
            
        except Exception as inner_error:
            logger.error(f"ERROR PROCESSING WEBHOOK DETAILS: {str(inner_error)}")
            import traceback
            logger.error(f"INNER ERROR TRACEBACK: {traceback.format_exc()}")
            
            # Always provide a response to Twilio regardless of errors
            resp.message("Thank you for your message. We'll respond shortly. (Error handled)")
        
        # Return the TwiML response
        return str(resp)
            
    except Exception as e:
        logger.error(f"ERROR PROCESSING BUSINESS-SPECIFIC WEBHOOK: {str(e)}")
        import traceback
        logger.error(f"TRACEBACK: {traceback.format_exc()}")
        
        # Always return a valid TwiML response even in case of errors
        resp = MessagingResponse()
        resp.message("Thank you for your message. Our team will respond shortly.")
        return str(resp)

@webhooks.route('/webhook-test', methods=['GET', 'POST'])
def webhook_test():
    """Simple test endpoint for Twilio webhook verification."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("WEBHOOK TEST ENDPOINT HIT")
    logger.info(f"Method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    if request.method == 'POST':
        logger.info(f"Form data: {dict(request.form)}")
    else:
        logger.info(f"Query params: {dict(request.args)}")
    
    # Create a simple TwiML response
    resp = MessagingResponse()
    resp.message("Your webhook test is working! This confirms Twilio can reach your server.")
    
    logger.info("Returning webhook test response")
    return str(resp)
