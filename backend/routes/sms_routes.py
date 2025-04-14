from flask import Blueprint, request, jsonify
from services.sms_processor import SMSProcessor
from models.workflow import Workflow
from twilio.twiml.messaging_response import MessagingResponse
from utils.message_quality import MessageQualityAnalyzer
from utils.cost_tracking import CostTracker
import logging

sms_bp = Blueprint('sms_bp', __name__)

# Initialize services
quality_analyzer = MessageQualityAnalyzer()
cost_tracker = CostTracker()

# Cache for SMS processors to avoid recreating them for each message
sms_processors = {}

def get_sms_processor(workflow_id: str) -> SMSProcessor:
    """Get or create an SMS processor for a workflow"""
    if workflow_id not in sms_processors:
        try:
            # Get workflow from database
            workflow = Workflow.query.get_or_404(workflow_id)
            
            # Create processor with workflow-specific configuration
            sms_processors[workflow_id] = SMSProcessor(
                business_id=workflow.client_id,
                workflow_id=workflow_id,
                workflow_name=workflow.name,
                config=workflow.actions.get('sms', {}),
                quality_analyzer=quality_analyzer,
                cost_tracker=cost_tracker
            )
            
            logging.info(f"Created new SMS processor for workflow {workflow_id}")
        except Exception as e:
            logging.error(f"Failed to create SMS processor for workflow {workflow_id}: {str(e)}")
            raise
    
    return sms_processors[workflow_id]

@sms_bp.route('/api/sms/webhook/<workflow_id>', methods=['POST'])
async def sms_webhook(workflow_id):
    """Handle incoming SMS messages for a specific workflow"""
    try:
        # Get message details from Twilio webhook
        from_number = request.values.get('From')
        message_body = request.values.get('Body')
        message_sid = request.values.get('MessageSid')
        
        if not from_number or not message_body:
            logging.error(f"Missing parameters for workflow {workflow_id}")
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get processor for this workflow
        processor = get_sms_processor(workflow_id)
        
        # Process the message with TwiML response
        result = await processor.process_incoming_message(
            from_number=from_number,
            message_body=message_body,
            use_twiml=True  # Use TwiML response instead of direct API call
        )
        
        # Create TwiML response
        twiml = MessagingResponse()
        
        # Only add message to TwiML if it wasn't sent via API
        if not result.sent_via_api and result.response:
            twiml.message(result.response)
        
        return str(twiml)
        
    except Exception as e:
        logging.error(f"Webhook error for workflow {workflow_id}: {str(e)}")
        # Return a generic error message to avoid exposing internal details
        twiml = MessagingResponse()
        twiml.message("We're sorry, but we couldn't process your message at this time. Please try again later.")
        return str(twiml)

@sms_bp.route('/api/sms/status/<workflow_id>', methods=['POST'])
def status_webhook(workflow_id):
    """Handle message status updates for a specific workflow"""
    try:
        message_sid = request.values.get('MessageSid')
        message_status = request.values.get('MessageStatus')
        error_code = request.values.get('ErrorCode')
        
        if not message_sid or not message_status:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get processor for this workflow
        processor = get_sms_processor(workflow_id)
        
        # Process the status update
        processor.process_delivery_status(
            message_sid=message_sid,
            status=message_status,
            error_code=error_code
        )
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Status webhook error for workflow {workflow_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@sms_bp.route('/api/sms/reset-cache', methods=['POST'])
def reset_processor_cache():
    """Reset the SMS processor cache when workflow configuration changes"""
    try:
        workflow_id = request.json.get('workflowId')
        
        if workflow_id:
            # Reset specific workflow
            if workflow_id in sms_processors:
                del sms_processors[workflow_id]
                logging.info(f"Reset SMS processor cache for workflow {workflow_id}")
        else:
            # Reset all processors
            sms_processors.clear()
            logging.info("Reset all SMS processor caches")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Error resetting processor cache: {str(e)}")
        return jsonify({'error': 'Failed to reset cache'}), 500

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
