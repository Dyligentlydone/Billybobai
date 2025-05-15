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
from ..db import db
from app.models.message import Message, MessageDirection, MessageChannel, MessageStatus
from datetime import datetime
import uuid
from config.database import SessionLocal

# Set up logging
logger = logging.getLogger(__name__)

webhooks = Blueprint('flask_webhooks', __name__)

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
            from app.models.business import Business
            from app.models.workflow import Workflow
            from app.models.sms_consent import SMSConsent
            
            logger.info("Attempting database query for business and workflow")
            
            # Check if business exists
            try:
                # Use the SQLAlchemy model directly instead of db.session.query
                business = Business.query.filter_by(id=business_id).first()
                logger.info(f"Business query completed: {'Found' if business else 'Not found'}")
            except Exception as db_error:
                logger.error(f"Database error querying business: {str(db_error)}")
                import traceback
                logger.error(f"TRACEBACK: {traceback.format_exc()}")
                resp.message("Thank you for your message. We'll get back to you soon. (Database error)")
                return str(resp)
            
            if not business:
                logger.error(f"Business not found with ID: {business_id}")
                # Always return a valid TwiML response even when business not found
                resp.message(f"Thank you for your message. We'll get back to you soon. (Business ID: {business_id} not found)")
                return str(resp)
            
            logger.info(f"Found business: {business.name if hasattr(business, 'name') else business.id}")
            
            # Get active workflow for this business
            workflow = Workflow.query.filter_by(
                business_id=business_id,
                status='ACTIVE'
            ).first()
            
            if not workflow:
                logger.error(f"NO ACTIVE WORKFLOW FOUND FOR BUSINESS ID: {business_id}")
                # Always return a valid TwiML response even when workflow not found
                resp.message("Thank you for your message. A representative will get back to you soon. (No active workflow)")
                return str(resp)
            
            # --------------------------------------------------
            # SMS Consent Handling
            # --------------------------------------------------
            logger.info(f"Checking consent status for {from_number} with business {business_id}")
            consent_record = SMSConsent.query.filter_by(
                phone_number=from_number,
                business_id=business_id
            ).first()
            logger.info(f"Existing consent record: {consent_record}")

            if not consent_record:
                logger.info("No consent record found, creating new one")
                try:
                    # Create new consent record the proper way with SQLAlchemy ORM
                    if not business or not hasattr(business, 'id'):
                        logger.error("Cannot create consent record: Business object is invalid")
                        resp.message("An error occurred. Please try again later.")
                        return str(resp)
                    
                    # Create a new consent record with proper values
                    new_consent = SMSConsent(
                        phone_number=from_number,
                        business_id=business_id,
                        status='PENDING'
                    )
                    
                    # Add and commit
                    logger.info(f"Adding new consent record: {new_consent}")
                    db.session.add(new_consent)
                    db.session.commit()
                    logger.info("Successfully created consent record")
                    
                    # Fetch the record we just created to confirm
                    consent_record = SMSConsent.query.filter_by(
                        phone_number=from_number,
                        business_id=business_id
                    ).first()
                    
                    # Safety check - verify the record exists
                    if not consent_record:
                        logger.error("Failed to retrieve newly created consent record")
                        resp.message("An error occurred. Please try again later.")
                        return str(resp)
                    
                    logger.info(f"Confirmed new consent record: {consent_record}")
                except Exception as e:
                    # Log the error with full traceback
                    logger.error(f"Failed to create consent record: {str(e)}")
                    import traceback
                    logger.error(f"Exception traceback: {traceback.format_exc()}")
                    
                    # Return error message instead of proceeding with a dummy record
                    resp.message("An error occurred with opt-in tracking. Please try again later.")
                    return str(resp)

            # Handle explicit YES/STOP replies
            body_upper = body.strip().upper() if body else ''

            if body_upper == 'YES':
                if consent_record.status != 'CONFIRMED':
                    consent_record.status = 'CONFIRMED'
                    db.session.commit()
                resp.message("Thanks! You've opted in to receive SMS updates. Reply STOP to opt out anytime.")
                return str(resp)

            if body_upper == 'STOP':
                if consent_record.status != 'DECLINED':
                    consent_record.status = 'DECLINED'
                    db.session.commit()
                resp.message("You have been opted out and will no longer receive automated SMS. Reply YES to opt back in.")
                return str(resp)

            # The consent record exists at this point, check opt-out status
            if consent_record.status == 'DECLINED':
                resp.message("You are currently opted out of SMS messages. Reply YES to opt back in.")
                return str(resp)

            # Flag for opt-in prompt if consent still pending (we will append after AI response)
            include_opt_in_prompt = consent_record.status == 'PENDING'

            # Process the message using the AI service
            if body:
                global ai_service
                # Initialize AI service if needed
                if ai_service is None:
                    from ..services.ai_service import AIService
                    ai_service = AIService()
                    logger.info("AI service initialized for SMS processing")
                
                # Check for conversation context to determine which sections to include
                # Find recent messages with this phone number for this business
                try:
                    # Use db.session.query instead of Message.query
                    recent_messages = db.session.query(Message).filter_by(
                        phone_number=from_number, 
                        workflow_id=workflow.id
                    ).order_by(Message.created_at.desc()).limit(10).all()
                except Exception as msg_error:
                    logger.error(f"Error querying message history: {str(msg_error)}")
                    recent_messages = []
                
                # Determine conversation context
                is_first_message = len(recent_messages) == 0
                
                # Look at the most recent message timestamps to determine if this is a new conversation
                # (e.g., if more than 30 minutes passed since the last message)
                conversation_timeout_minutes = workflow.actions.get('response', {}).get('conversationTimeoutMinutes', 30)
                is_new_conversation = is_first_message
                current_conversation_id = None
                
                if not is_first_message:
                    last_message_time = recent_messages[0].created_at
                    time_difference = (datetime.utcnow() - last_message_time).total_seconds() / 60
                    is_new_conversation = time_difference > conversation_timeout_minutes
                    # Use existing conversation ID if within timeout
                    if not is_new_conversation and recent_messages[0].conversation_id:
                        current_conversation_id = recent_messages[0].conversation_id
                
                # Generate new conversation ID if needed
                if is_new_conversation or not current_conversation_id:
                    import uuid
                    current_conversation_id = str(uuid.uuid4())
                
                # Now determine which message structure sections to include
                include_greeting = is_new_conversation
                include_next_steps = False  # The AI will tell us if next steps are needed
                include_sign_off = False    # The AI will tell us if sign off is appropriate
                
                try:
                    # Store incoming message in the database
                    session = SessionLocal()
                    try:
                        incoming_message = Message(
                            workflow_id=workflow.id,
                            direction=MessageDirection.INBOUND,
                            channel=MessageChannel.SMS,
                            content=body,
                            phone_number=from_number,
                            conversation_id=current_conversation_id,
                            is_first_in_conversation=is_new_conversation,
                            status=MessageStatus.DELIVERED  # Inbound messages are already delivered
                        )
                        session.add(incoming_message)
                        session.commit()
                        incoming_message_id = incoming_message.id
                    except Exception as db_error:
                        import traceback
                        error_trace = traceback.format_exc()
                        logger.error(f"Error storing incoming message: {str(db_error)}")
                        logger.error(f"Detailed error traceback: {error_trace}")
                        logger.error(f"Message data: workflow_id={workflow.id}, phone={from_number}, content={body}")
                        incoming_message_id = None
                        session.rollback()
                    finally:
                        session.close()
                    
                    # Prepare conversation history for the AI
                    conversation_history = []
                    if not is_new_conversation and len(recent_messages) > 0:
                        # Convert to format expected by AI service
                        for msg in recent_messages[:5]:  # Last 5 messages
                            conversation_history.append({
                                "role": "user" if msg.direction == MessageDirection.INBOUND else "assistant",
                                "content": msg.content
                            })
                        # Reverse to get chronological order
                        conversation_history.reverse()
                    
                    # Generate AI response based on workflow configuration
                    logger.info("CALLING AI SERVICE TO GENERATE RESPONSE...")
                    workflow_response = ai_service.analyze_requirements(
                        body, 
                        workflow.actions, 
                        conversation_history=conversation_history,
                        is_new_conversation=is_new_conversation
                    )
                    logger.info(f"AI SERVICE RESPONSE: {workflow_response}")
                    
                    # Get response text from AI or fallback message
                    ai_response_text = workflow_response.get('message', '')
                    
                    # Check if AI detected need for next steps or sign off
                    if isinstance(workflow_response, dict):
                        include_next_steps = workflow_response.get('include_next_steps', False)
                        include_sign_off = workflow_response.get('include_sign_off', False)
                    
                    # Apply message structure template from workflow configuration
                    response_text = ""
                    message_structure = workflow.actions.get('response', {}).get('messageStructure', [])
                    
                    # Check if there's a defined message structure to use
                    if message_structure and isinstance(message_structure, list):
                        logger.info(f"Using configured message structure with {len(message_structure)} sections")
                        
                        # Build response using the configured structure
                        for section in message_structure:
                            if section.get('enabled', True):
                                section_name = section.get('name', '').lower()
                                section_content = section.get('defaultContent', '')
                                
                                # Skip sections based on conversation context
                                if section_name == 'greeting' and not include_greeting:
                                    continue
                                elif section_name == 'next steps' and not include_next_steps:
                                    continue
                                elif section_name == 'sign off' and not include_sign_off:
                                    continue
                                
                                # If this is the main content section, use the AI response
                                if section_name == 'main content':
                                    section_text = ai_response_text or section_content
                                else:
                                    section_text = section_content
                                
                                # Add the section to the response if it has content
                                if section_text:
                                    # Add a line break between sections for readability
                                    if response_text:
                                        response_text += "\n"
                                    response_text += section_text
                        
                        # Trim any extra spaces
                        response_text = response_text.strip()
                        logger.info(f"Applied template structure, final response: {response_text[:50]}...")
                    else:
                        # Fall back to just the AI response if no structure defined
                        response_text = ai_response_text or (
                            workflow.actions.get('twilio', {}).get('fallbackMessage') or
                            workflow.actions.get('response', {}).get('fallbackMessage') or
                            "Thank you for your message. We'll respond shortly."
                        )
                     
                    # Append opt-in prompt (if consent pending)
                    if include_opt_in_prompt:
                        opt_in_prompt = (
                            workflow.actions.get('twilio', {}).get('optInPrompt') or
                            f"Reply YES to receive SMS updates. Reply STOP to opt out."
                        )
                        # Ensure spacing/newline separation
                        if response_text:
                            response_text = f"{response_text}\n\n{opt_in_prompt}"
                        else:
                            response_text = opt_in_prompt
                    
                    # Add the response to the TwiML
                    resp.message(response_text)
                    
                    # Store outgoing message in the database
                    try:
                        session = SessionLocal()
                        outgoing_message = Message(
                            workflow_id=workflow.id,
                            direction=MessageDirection.OUTBOUND,
                            channel=MessageChannel.SMS,
                            content=response_text,
                            phone_number=from_number,
                            conversation_id=current_conversation_id,
                            response_to_message_id=incoming_message_id if incoming_message_id else None,
                            status=MessageStatus.SENT
                        )
                        session.add(outgoing_message)
                        session.commit()
                    except Exception as db_error:
                        logger.error(f"Error storing outgoing message: {str(db_error)}")
                    finally:
                        session.close()
                    
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
