from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from services.sms_processor import SMSProcessor
from services.opt_out_handler import OptOutHandler
from app.db import db
from app.models.workflow import Workflow
from utils.message_quality import MessageQualityAnalyzer
from utils.cost_tracking import CostTracker
import logging

sms_bp = Blueprint('sms_bp', __name__)

# Initialize services
quality_analyzer = MessageQualityAnalyzer()
cost_tracker = CostTracker()

# Cache for SMS processors
processor_cache = {}

def get_sms_processor(workflow_id: str) -> SMSProcessor:
    """Get or create an SMS processor for a workflow"""
    if workflow_id not in processor_cache:
        try:
            # Get workflow from database
            workflow = Workflow.query.get_or_404(workflow_id)
            
            # Create processor with workflow-specific configuration
            processor_cache[workflow_id] = SMSProcessor(
                business_id=workflow.business_id,
                workflow_id=workflow_id,
                workflow_name=workflow.name,
                config=workflow.actions.get('twilio', {}),
                quality_analyzer=quality_analyzer,
                cost_tracker=cost_tracker
            )
            
            logging.info(f"Created new SMS processor for workflow {workflow_id}")
        except Exception as e:
            logging.error(f"Failed to create SMS processor for workflow {workflow_id}: {str(e)}")
            raise
    
    return processor_cache[workflow_id]

def get_opt_out_handler():
    """Get an OptOutHandler instance"""
    return OptOutHandler(db)

@sms_bp.route('/api/sms/webhook/<workflow_id>', methods=['POST'])
async def sms_webhook(workflow_id):
    """Handle incoming SMS messages for a specific workflow"""
    processor = get_sms_processor(workflow_id)
    opt_out_handler = get_opt_out_handler()
    
    # Get message details from Twilio webhook
    from_number = request.values.get('From', '')
    message_body = request.values.get('Body', '').strip()
    business_id = processor.get_business_id()
    
    # Check for opt-out
    if opt_out_handler.is_opt_out_message(message_body):
        await opt_out_handler.handle_opt_out(from_number, business_id)
        resp = MessagingResponse()
        resp.message("You have been unsubscribed from future messages. Reply START to opt back in.")
        return str(resp)
    
    # Check for opt-in
    if opt_out_handler.is_opt_in_message(message_body):
        was_opted_out = await opt_out_handler.is_opted_out(from_number, business_id)
        if was_opted_out:
            await opt_out_handler.handle_opt_in(from_number, business_id)
            resp = MessagingResponse()
            resp.message("You have been successfully re-subscribed to receive messages from Dyligent.")
            return str(resp)
    
    # Check if number is opted out
    if await opt_out_handler.is_opted_out(from_number, business_id):
        resp = MessagingResponse()
        resp.message("You are currently unsubscribed. Reply START to receive messages again.")
        return str(resp)
    
    # Process the message normally
    logging.info(f"[SMS_WEBHOOK] Processing incoming message: workflow_id={workflow_id}, message_body={message_body}")
    result = await processor.process_incoming_message(
        from_number=from_number,
        message_body=message_body,
        use_twiml=True  # Use TwiML response instead of direct API call
    )
    logging.info(f"[SMS_WEBHOOK] ProcessingResult: sent_via_api={getattr(result, 'sent_via_api', None)}, response={getattr(result, 'response', None)}")
    
    # Create TwiML response
    twiml = MessagingResponse()
    
    # Only add message to TwiML if it wasn't sent via API
    if not result.sent_via_api and result.response:
        twiml.message(result.response)
    
    return str(twiml)

@sms_bp.route('/api/sms/status/<workflow_id>', methods=['POST'])
def status_webhook(workflow_id):
    """Handle message status updates for a specific workflow"""
    processor = get_sms_processor(workflow_id)
    
    message_sid = request.values.get('MessageSid')
    message_status = request.values.get('MessageStatus')
    error_code = request.values.get('ErrorCode')
    
    if not message_sid or not message_status:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Process the status update
    processor.process_delivery_status(
        message_sid=message_sid,
        status=message_status,
        error_code=error_code
    )
    
    return jsonify({'status': 'success'})

@sms_bp.route('/api/sms/opt-outs/<int:business_id>', methods=['GET'])
async def get_opt_outs(business_id):
    """Get opt-out statistics for a business"""
    opt_out_handler = get_opt_out_handler()
    stats = await opt_out_handler.get_opt_out_stats(business_id)
    return jsonify(stats)

@sms_bp.route('/api/sms/reset-cache', methods=['POST'])
def reset_processor_cache():
    """Reset the SMS processor cache"""
    global processor_cache
    processor_cache = {}
    return jsonify({'status': 'success'})

@sms_bp.route('/api/sms/validate-webhook/<workflow_id>', methods=['GET'])
def validate_webhook(workflow_id):
    """Validate that the webhook is properly configured"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        
        # Basic validation response
        return jsonify({
            'status': 'success',
            'message': 'Webhook endpoint is valid',
            'workflow_id': workflow_id,
            'url': f"/api/sms/webhook/{workflow_id}"
        })
        
    except Exception as e:
        logging.error(f"Webhook validation error for workflow {workflow_id}: {str(e)}")
        return jsonify({'error': 'Invalid workflow ID'}), 404
