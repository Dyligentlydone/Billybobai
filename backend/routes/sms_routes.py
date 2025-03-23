from flask import Blueprint, request, jsonify
from services.sms_processor import SMSProcessor
from app.models.workflow import Workflow
from twilio.twiml.messaging_response import MessagingResponse

sms_bp = Blueprint('sms_bp', __name__)

# Cache for SMS processors to avoid recreating them for each message
sms_processors = {}

def get_sms_processor(workflow_id: str) -> SMSProcessor:
    """Get or create an SMS processor for a workflow"""
    if workflow_id not in sms_processors:
        # Get workflow from database
        workflow = Workflow.query.get_or_404(workflow_id)
        
        # Create processor
        sms_processors[workflow_id] = SMSProcessor(
            business_id=workflow.client_id,
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            config=workflow.actions.get('sms', {})  # Get SMS-specific config
        )
    
    return sms_processors[workflow_id]

@sms_bp.route('/api/sms/webhook/<workflow_id>', methods=['POST'])
async def sms_webhook(workflow_id):
    """Handle incoming SMS messages"""
    # Get message details from Twilio webhook
    from_number = request.values.get('From')
    message_body = request.values.get('Body')
    
    if not from_number or not message_body:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get processor for this workflow
    processor = get_sms_processor(workflow_id)
    
    # Process the message
    success, error = await processor.process_incoming_message(from_number, message_body)
    
    if not success:
        # Log the error (you might want to add proper logging)
        print(f"Error processing message: {error}")
    
    # Return empty TwiML response (we're handling the response asynchronously)
    response = MessagingResponse()
    return str(response)

@sms_bp.route('/api/sms/status/<workflow_id>', methods=['POST'])
def status_webhook(workflow_id):
    """Handle message status updates"""
    message_sid = request.values.get('MessageSid')
    message_status = request.values.get('MessageStatus')
    
    if not message_sid or not message_status:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get processor for this workflow
    processor = get_sms_processor(workflow_id)
    
    # Process the status update
    processor.process_delivery_status(message_sid, message_status)
    
    return jsonify({'status': 'success'})

@sms_bp.route('/api/sms/reset-cache', methods=['POST'])
def reset_processor_cache():
    """Reset the SMS processor cache (useful when workflow config changes)"""
    workflow_id = request.json.get('workflowId')
    
    if workflow_id:
        # Reset specific workflow
        if workflow_id in sms_processors:
            del sms_processors[workflow_id]
    else:
        # Reset all
        sms_processors.clear()
    
    return jsonify({'status': 'success'})
